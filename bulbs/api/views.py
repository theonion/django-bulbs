"""API Views and ViewSets"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.loading import get_models
from django.http import Http404
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from firebase_token_generator import create_token
import elasticsearch
from rest_framework import (
    decorators,
    filters,
    status,
    viewsets,
    routers
)
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from elastimorphic.models import polymorphic_indexable_registry
from elasticutils.contrib.django import get_es

from bulbs.content.models import Content, Tag, LogEntry, FeatureType, ObfuscatedUrlInfo
from bulbs.content.serializers import (
    LogEntrySerializer, PolymorphicContentSerializer,
    TagSerializer, UserSerializer, FeatureTypeSerializer,
    ObfuscatedUrlInfoSerializer
)
from bulbs.contributions.serializers import ContributionSerializer
from bulbs.contributions.models import Contribution
from .mixins import UncachedResponse
from .permissions import CanEditContent, CanPublishContent


class ContentViewSet(UncachedResponse, viewsets.ModelViewSet):
    """
    uncached viewset for the `bulbs.content.Content` model
    """

    model = Content
    queryset = Content.objects.select_related("tags").all()
    serializer_class = PolymorphicContentSerializer
    include_base_doctype = False
    paginate_by = 20
    filter_fields = ("tags", "authors", "feature_types", "published", "types")
    search_fields = ("title", "description")
    permission_classes = [IsAdminUser, CanEditContent]

    def get_serializer_class(self):
        """gets the class type of the serializer

        :return: `rest_framework.Serializer`
        """
        klass = None

        if getattr(self, "object", None):
            klass = self.object.__class__
        elif "doctype" in self.request.REQUEST:
            try:
                klass = Content.get_doctypes()[self.request.REQUEST["doctype"]]
            except KeyError:
                raise Http404

        if hasattr(klass, "get_serializer_class"):
            return klass.get_serializer_class()

        # TODO: fix deprecation warning here -- `get_serializer_class` is going away soon!
        return super(ContentViewSet, self).get_serializer_class()

    def post_save(self, obj, created=False):
        """indexes the object to ElasticSearch after any save function (POST/PUT)

        :param obj: instance of the saved object
        :param created: boolean expressing if object is newly created (`False` if updated)
        :return: `rest_framework.viewset.ModelViewSet.post_save`
        """
        from bulbs.content.tasks import index

        index.delay(obj.polymorphic_ctype_id, obj.pk)

        message = "Created" if created else "Saved"
        LogEntry.objects.log(self.request.user, obj, message)
        return super(ContentViewSet, self).post_save(obj, created=created)

    def list(self, request, *args, **kwargs):
        """I'm overriding this so that the listing pages can be driven from ElasticSearch

        :param request: a WSGI request object
        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """

        # check for a text query
        search_kwargs = {"published": False}
        search_query = request.QUERY_PARAMS.get("search", None)
        if search_query:
            search_kwargs["query"] = search_query

        if "before" in request.QUERY_PARAMS:
            search_kwargs["before"] = parse_datetime(request.QUERY_PARAMS["before"])

        if "after" in request.QUERY_PARAMS:
            search_kwargs["after"] = parse_datetime(request.QUERY_PARAMS["after"])

        if "status" in request.QUERY_PARAMS:
            search_kwargs["status"] = request.QUERY_PARAMS["status"]
            del search_kwargs["published"]

        # filter on specific fields using `filter_fields` on your view
        filter_fields = getattr(self, "filter_fields", None)
        if filter_fields:
            for field_name in filter_fields:
                filter_query = request.QUERY_PARAMS.getlist(field_name, None)
                if filter_query:

                    # We need to figure out how to match on a slug, not a name
                    if field_name == "feature_types":
                        filter_query = [slugify(f) for f in filter_query]

                    search_kwargs[field_name] = filter_query

        self.object_list = self.model.search_objects.search(**search_kwargs).full()

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

    @decorators.action(permission_classes=[CanPublishContent])
    def publish(self, request, **kwargs):
        """sets the `published` value of the `Content`

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        content = self.get_object()

        if "published" in request.DATA:
            if not request.DATA["published"]:
                content.published = None
            else:
                publish_dt = parse_datetime(request.DATA["published"])
                if publish_dt:
                    publish_dt = publish_dt.astimezone(timezone.utc)
                else:
                    publish_dt = None
                content.published = publish_dt
        else:
            content.published = timezone.now()

        content.save()
        LogEntry.objects.log(request.user, content, content.get_status())
        return Response({"status": content.get_status(), "published": content.published})

    @decorators.action(permission_classes=[CanPublishContent])
    def trash(self, request, **kwargs):
        """destroys a `Content` instance and removes it from the ElasticSearch index

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        :raise: 404
        """
        content = self.get_object()

        content.indexed = False
        content.save()

        es = get_es(urls=settings.ES_URLS)
        try:
            es.delete(index=content.get_index_name(), doc_type=content.get_mapping_type_name(),
                      id=content.id)
            LogEntry.objects.log(request.user, content, "Trashed")
            return Response({"status": "Trashed"})
        except elasticsearch.exceptions.NotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @decorators.link()
    def status(self, request, **kwargs):
        """This endpoint returns a status text, currently one of:
          - "Draft" (If no publish date is set, and no item exists in the editor queue)
          - "Waiting for Editor" (If no publish date is set, and an item exists in the editor queue)
          - "Published" (The published date is in the past)
          - "Scheduled" (The published date is set in the future)

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        content = self.get_object()
        return Response({"status": content.get_status()})

    @detail_route(methods=["post", "get"])
    def contributions(self, request, **kwargs):
        """gets or adds contributions

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        # Check if the contribution app is installed
        if Contribution not in get_models():
            return Response([])
        queryset = Contribution.objects.filter(content=self.get_object())
        if request.method == "POST":
            serializer = ContributionSerializer(
                queryset,
                data=request.DATA,
                many=True,
                allow_add_remove=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = ContributionSerializer(queryset, many=True)
            return Response(serializer.data)

    @detail_route(methods=["post"], permission_classes=[CanEditContent])
    def create_token(self, request, **kwargs):
        """Create a new obfuscated url info to use for accessing unpublished content.

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """

        data = ObfuscatedUrlInfoSerializer(ObfuscatedUrlInfo.objects.create(
            content=self.get_object(),
            create_date=request.DATA["create_date"],
            expire_date=request.DATA["expire_date"]
        )).data

        return Response(data, status=status.HTTP_200_OK, content_type="application/json")

    @detail_route(methods=["get"], permission_classes=[CanEditContent])
    def list_tokens(self, request, **kwargs):
        """List all tokens for this content instance.

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """

        # no date checking is done here to make it more obvious if there's an issue with the
        # number of records. Date filtering will be done on the frontend.
        infos = [ObfuscatedUrlInfoSerializer(info).data
                 for info in ObfuscatedUrlInfo.objects.filter(content=self.get_object())]
        return Response(infos, status=status.HTTP_200_OK, content_type="application/json")


class TagViewSet(UncachedResponse, viewsets.ReadOnlyModelViewSet):
    """
    uncached viewset for the `bulbs.content.Tag` model
    """

    model = Tag
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ("name",)
    paginate_by = 50

    def list(self, request, *args, **kwargs):
        """I'm overriding this so that the listing pages can be driven from ElasticSearch

        :param request: a WSGI request object
        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """

        search_query = Tag.search_objects.s()
        if "search" in request.REQUEST:
            search_query = search_query.query(
                name__match_phrase=request.REQUEST["search"], should=True
            ).query(
                name__term=request.REQUEST["search"], should=True
            )

        if "types" in request.REQUEST:
            search_query = search_query.doctypes(*request.REQUEST.getlist("types"))

        # HACK ALERT. I changed the edge ngram to go from 3 to 10, so "TV" got screwed
        if len(request.REQUEST.get("search", [])) < 3:
            self.object_list = Tag.objects.filter(
                name__istartswith=request.REQUEST["search"].lower()
            )
            if "types" in request.REQUEST:
                type_classes = [polymorphic_indexable_registry.all_models[type_name] for type_name
                                in request.REQUEST.getlist("types")]
                print(type_classes)
                self.object_list = self.object_list.instance_of(*type_classes)
        else:
            self.object_list = search_query.full()

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)


class UserViewSet(UncachedResponse, viewsets.ModelViewSet):
    """
    uncached viewset for the User model -- User can be whatever is defined as the default system
    user model (`auth.User` or any other custom model)
    """

    model = get_user_model()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("first_name", "last_name", "username")
    paginate_by = 20


class LogEntryViewSet(UncachedResponse, viewsets.ModelViewSet):
    """
    uncached viewset for `bulbs.content.LogEntry` model
    """

    model = LogEntry
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        """creates the base queryset object for the serializer

        :return: an instance of `django.db.models.QuerySet`
        """
        qs = super(LogEntryViewSet, self).get_queryset()
        content_id = self.request.QUERY_PARAMS.get("content", None)
        if content_id:
            qs = qs.filter(object_id=content_id)
        return qs

    def create(self, request, *args, **kwargs):
        """
        Grabbing the user from request.user, and the rest of the method
        is the same as ModelViewSet.create().

        :param request: a WSGI request object
        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        :raise: 400
        """
        data = request.DATA.copy()
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorViewSet(UncachedResponse, viewsets.ReadOnlyModelViewSet):
    """
    uncached readonly viewset for the system user model limited to author groups and permissions
    """

    model = get_user_model()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("first_name", "last_name", "username")

    def get_queryset(self):
        """created the base queryset object for the serializer limited to users within the authors
        groups and having `is_staff`

        :return: `django.db.models.QuerySet`
        """
        author_filter = getattr(settings, "BULBS_AUTHOR_FILTER", {"is_staff": True})
        queryset = self.model.objects.filter(**author_filter).distinct()
        return queryset


class FeatureTypeViewSet(UncachedResponse, viewsets.ReadOnlyModelViewSet):
    """
    uncached readonly viewset for the `bulbs.content.FeatureType` model
    """

    model = FeatureType
    serializer_class = FeatureTypeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", )


class MeViewSet(UncachedResponse, viewsets.ReadOnlyModelViewSet):
    """
    uncached readonly viewset for users to get information about themselves
    """

    def retrieve(self, request, *args, **kwargs):
        """gets basic information about the user

        :param request: a WSGI request object
        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        data = UserSerializer().to_native(request.user)

        # add superuser flag only if user is a superuser, putting it here so users can only
        # tell if they are themselves superusers
        if request.user.is_superuser:
            data['is_superuser'] = True

        # attempt to add a firebase token if we have a firebase secret
        secret = getattr(settings, 'FIREBASE_SECRET', None)
        if secret:
            # use firebase auth to provide auth variables to firebase security api
            firebase_auth_payload = {
                'id': request.user.pk,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff
            }
            data['firebase_token'] = create_token(secret, firebase_auth_payload)

        return Response(data)


class DoctypeViewSet(viewsets.ViewSet):
    """Searches doctypes of a model."""
    model = Content

    def list(self, request):
        """Search the doctypes for this model."""
        query = request.QUERY_PARAMS.get("search", "")
        results = []
        doctypes = self.model.get_doctypes()
        for doctype, klass in doctypes.items():
            name = klass._meta.verbose_name
            if query.lower() in name.lower():
                results.append(dict(
                    name=name,
                    doctype=doctype
                ))
        results.sort(key=lambda x: x["name"])
        return Response(dict(results=results))


# api router for aforementioned/defined viewsets
# note: me view is registered in urls.py
api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"content", ContentViewSet, base_name="content")
api_v1_router.register(r"doctype", DoctypeViewSet, base_name="doctype")
api_v1_router.register(r"tag", TagViewSet, base_name="tag")
api_v1_router.register(r"log", LogEntryViewSet, base_name="logentry")
api_v1_router.register(r"author", AuthorViewSet, base_name="author")
api_v1_router.register(r"feature-type", FeatureTypeViewSet, base_name="feature-type")
api_v1_router.register(r"user", UserViewSet, base_name="user")
