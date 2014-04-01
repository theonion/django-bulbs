"""API Views and ViewSets"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework import (
    decorators,
    filters,
    status,
    viewsets,
    routers
)

from rest_framework.response import Response

from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from bulbs.content.models import Content, Tag, LogEntry
from bulbs.content.serializers import (
    LogEntrySerializer, PolymorphicContentSerializer,
    TagSerializer, UserSerializer
)
from .filters import (
    TagSearchFilter, AuthorSearchFilter,
    DateSearchFilter, DoctypeFilter
)

from .mixins import UncachedResponse


class ContentViewSet(UncachedResponse, viewsets.ModelViewSet):
    model = Content
    queryset = Content.objects.select_related("tags").all()
    serializer_class = PolymorphicContentSerializer
    include_base_doctype = False
    paginate_by = 20
    filter_backends = (
        filters.SearchFilter, filters.OrderingFilter,
        TagSearchFilter, AuthorSearchFilter, DateSearchFilter, DoctypeFilter
    )
    filter_fields = ("tags", "authors", "feature_types", "published", "types")
    search_fields = ("title", "description")

    # TODO: "post_save"?

    def get_serializer_class(self):
        klass = None

        if hasattr(self, "object"):
            klass = self.object.__class__
        elif "doctype" in self.request.REQUEST:
            klass = Content.get_doctypes()[self.request.REQUEST["doctype"]]

        if hasattr(klass, "get_serializer_class"):
            return klass.get_serializer_class()

        return super(ContentViewSet, self).get_serializer_class()

    def post_save(self, obj, created=False):
        from bulbs.content.tasks import index
        index.delay(obj.polymorphic_ctype_id, obj.pk)

        message = "Created" if created else "Saved"
        LogEntry.objects.log(self.request.user, obj, message)
        return super(ContentViewSet, self).post_save(obj, created=created)

    def list(self, request, *args, **kwargs):
        """I'm overriding this so that the listing pages can be driven from ElasticSearch"""

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

    @decorators.action()
    def publish(self, request, **kwargs):
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

    @decorators.action()
    def trash(self, request, **kwargs):
        content = self.get_object()

        content.indexed = False
        content.save()

        es = get_es(urls=settings.ES_URLS)
        try:
            es.delete(content.get_index_name(), content.get_mapping_type_name(), content.id)
            LogEntry.objects.log(request.user, content, "Trashed")
            return Response({"status": "Trashed"})
        except ElasticHttpNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @decorators.link()
    def status(self, request, **kwargs):
        """This endpoint returns a status text, currently one of:
          - "Draft" (If no publish date is set, and no item exists in the editor queue)
          - "Waiting for Editor" (If no publish date is set, and an item exists in the editor queue)
          - "Published" (The published date is in the past)
          - "Scheduled" (The published date is set in the future)
        """
        content = self.get_object()
        return Response({"status": content.get_status()})

    # @decorators.list_route()
    def feature_types(self, request, **kwargs):
        query = self.model.search_objects.search(published=False)
        if "q" in request.QUERY_PARAMS:
            query = query.query(
                **{
                    "feature_type.name.autocomplete__match": request.QUERY_PARAMS["q"],
                    "should": True
                })
        facet_counts = query.facet_raw(
            feature_type={
                "terms": {
                    "field": "feature_type.name",
                    "size": 40
                }
            }
        ).facet_counts()

        facets = facet_counts["feature_type"]
        data = []
        for facet in facets:
            facet_data = {
                "name": facet["term"],
                "count": facet["count"]
            }
            data.append(facet_data)

        return Response(data)


class TagViewSet(UncachedResponse, viewsets.ReadOnlyModelViewSet):
    model = Tag
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name",)
    paginate_by = 50

    def list(self, request, *args, **kwargs):
        """I'm overriding this so that the listing pages can be driven from ElasticSearch"""

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
    model = get_user_model()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("first_name", "last_name", "username")
    paginate_by = 20


class LogEntryViewSet(UncachedResponse, viewsets.ModelViewSet):
    model = LogEntry
    serializer_class = LogEntrySerializer

    def get_queryset(self):
        qs = super(LogEntryViewSet, self).get_queryset()
        content_id = self.request.QUERY_PARAMS.get("content", None)
        if content_id:
            qs = qs.filter(object_id=content_id)
        return qs

    def create(self, request):
        """
        Grabbing the user from request.user, and the rest of the method
        is the same as ModelViewSet.create().
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

api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"content", ContentViewSet, base_name="content")
api_v1_router.register(r"log", LogEntryViewSet, base_name="logentry")
api_v1_router.register(r"user", UserViewSet, base_name="user")
