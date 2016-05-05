"""API Views and ViewSets"""

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve, Resolver404
from django.db.models.loading import get_models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from djes.apps import indexable_registry
import elasticsearch
from elasticsearch_dsl.query import Q
from elasticsearch_dsl import filter as es_filter
from firebase_token_generator import create_token
from rest_framework import (
    filters,
    status,
    viewsets,
    routers
)
from rest_framework.decorators import detail_route, list_route
from rest_framework.metadata import BaseMetadata
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from bulbs.content.custom_search import custom_search_model
from bulbs.content.filters import Authors
from bulbs.content.models import Content, Tag, LogEntry, FeatureType, ObfuscatedUrlInfo
from bulbs.content.serializers import (
    ContentSerializer, LogEntrySerializer, PolymorphicContentSerializer,
    TagSerializer, UserSerializer, FeatureTypeSerializer,
    ObfuscatedUrlInfoSerializer
)
from bulbs.contributions.tasks import run_contributor_email_report
from bulbs.contributions.models import Contribution
from bulbs.contributions.serializers import ContributionSerializer, ContributorReportSerializer
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.special_coverage.serializers import SpecialCoverageSerializer
from bulbs.utils.methods import get_query_params, get_request_data

from .mixins import UncachedResponse
from .permissions import CanEditContent, CanPublishContent


class ContentViewMetaData(BaseMetadata):
    def determine_metadata(self, request, view):
        return {
            'status': 'ok',
        }


class ContentViewSet(UncachedResponse, viewsets.ModelViewSet):
    """
    uncached viewset for the `bulbs.content.Content` model
    """

    model = Content
    queryset = Content.objects.all()
    serializer_class = PolymorphicContentSerializer
    include_base_doctype = False
    paginate_by = 20
    filter_fields = (
        "search", "before", "after", "status",
        "feature_types", "published", "tags",
        "authors", "types"
    )
    permission_classes = [IsAdminUser, CanEditContent]
    metadata_class = ContentViewMetaData

    def get_serializer_class(self):
        """gets the class type of the serializer

        :return: `rest_framework.Serializer`
        """
        klass = None

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            # Looks like this is a detail...
            klass = self.get_object().__class__
        elif "doctype" in self.request.REQUEST:
            base = self.model.get_base_class()
            doctypes = indexable_registry.families[base]
            try:
                klass = doctypes[self.request.REQUEST["doctype"]]
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
        """Modified list view to driving listing from ES"""
        search_kwargs = {"published": False}

        for field_name in ("before", "after", "status", "published"):

            if field_name in get_query_params(self.request):
                search_kwargs[field_name] = get_query_params(self.request).get(field_name)

        for field_name in ("tags", "types", "feature_types"):

            if field_name in get_query_params(self.request):
                search_kwargs[field_name] = get_query_params(self.request).getlist(field_name)

        if "search" in get_query_params(self.request):
            search_kwargs["query"] = get_query_params(self.request).get("search")

        queryset = self.model.search_objects.search(**search_kwargs)

        if "authors" in get_query_params(self.request):
            authors = get_query_params(self.request).getlist("authors")
            queryset = queryset.filter(Authors(authors))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(permission_classes=[CanPublishContent], methods=['post'])
    def publish(self, request, **kwargs):
        """sets the `published` value of the `Content`

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        content = self.get_object()

        if "published" in get_request_data(request):
            if not get_request_data(request)["published"]:
                content.published = None
            else:
                publish_dt = parse_datetime(get_request_data(request)["published"])
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

    @detail_route(permission_classes=[CanPublishContent], methods=['post'])
    def trash(self, request, **kwargs):
        """Psuedo-deletes a `Content` instance and removes it from the ElasticSearch index

        Content is not actually deleted, merely hidden by deleted from ES index.import

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """
        content = self.get_object()

        content.indexed = False
        content.save()

        LogEntry.objects.log(request.user, content, "Trashed")
        return Response({"status": "Trashed"})

    @detail_route(methods=["get"])
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

        content_pk = kwargs.get('pk', None)
        if content_pk is None:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        queryset = Contribution.search_objects.search().filter(
            es_filter.Term(**{'content.id': content_pk})
        )
        if request.method == "POST":
            serializer = ContributionSerializer(
                queryset[:queryset.count()].sort('id')[:25],
                data=get_request_data(request),
                many=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = ContributionSerializer(queryset[:queryset.count()].sort('id'), many=True)
            return Response(serializer.data)

    @detail_route(methods=["post"], permission_classes=[CanEditContent])
    def create_token(self, request, **kwargs):
        """Create a new obfuscated url info to use for accessing unpublished content.

        :param request: a WSGI request object
        :param kwargs: keyword arguments (optional)
        :return: `rest_framework.response.Response`
        """

        data = {
            "content": self.get_object().id,
            "create_date": get_request_data(request)["create_date"],
            "expire_date": get_request_data(request)["expire_date"]
        }
        serializer = ObfuscatedUrlInfoSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK, content_type="application/json")

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
    serializer_class = TagSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Tag.search_objects.search()
        if "search" in self.request.REQUEST:
            query_string = self.request.REQUEST["search"].lower()
            queryset = queryset.query(
                Q("match", name=query_string) | Q("match", **{"name.raw": query_string})
            )

        types = get_query_params(self.request).getlist("types", None)
        if types:
            queryset._doc_type = self.request.REQUEST["types"]
        return queryset


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
        qs = LogEntry.objects.all()
        content_id = get_query_params(self.request).get("content", None)
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
        data = get_request_data(request).copy()
        data["user"] = request.user.id
        serializer = self.get_serializer(data=data, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

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
    paginate_by = 50

    def get_queryset(self):
        queryset = FeatureType.search_objects.search()
        if "search" in self.request.REQUEST:
            query_string = self.request.REQUEST["search"].lower()
            queryset = queryset.query(
                Q("match", name=query_string) | Q("match", **{"name.raw": query_string})
            )
        return queryset


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
        data = UserSerializer().to_representation(request.user)

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


class ContentTypeViewSet(viewsets.ViewSet):
    """Searches doctypes of a model."""
    model = Content

    def list(self, request):
        """Search the doctypes for this model."""
        query = get_query_params(request).get("search", "")
        results = []
        base = self.model.get_base_class()
        doctypes = indexable_registry.families[base]
        for doctype, klass in doctypes.items():
            name = klass._meta.verbose_name.title()
            if query.lower() in name.lower():
                results.append(dict(
                    name=name,
                    doctype=doctype
                    ))
                results.sort(key=lambda x: x["name"])
        return Response(dict(results=results))


class ContentResolveViewSet(viewsets.ReadOnlyModelViewSet):
    """Retrieve content corresponding to absolute URL"""
    model = Content

    def list(self, request):
        url = get_query_params(self.request).get("url")
        if url:
            try:
                match = resolve(urlparse(url).path)
            except Resolver404:
                raise Http404("No content found matching UUID")

            content = get_object_or_404(Content, pk=match.kwargs.get('pk'))
            return Response(ContentSerializer(content).data)
        else:
            raise Http404('Must specify content "url" param')


class SpecialCoverageResolveViewSet(viewsets.ReadOnlyModelViewSet):
    """Retrieve special coverage containing specified content"""
    model = SpecialCoverage

    def list(self, request):
        content_id = get_query_params(self.request).get("content_id")
        if content_id:
            content = get_object_or_404(Content, pk=content_id)
            # Find special coverage via percolator
            special_coverage_filter = {
                "filter": {
                    "prefix": {"_id": "specialcoverage"}
                }
            }
            search_objects = type(content).search_objects
            results = search_objects.client.percolate(
                index=search_objects.mapping.index,
                doc_type=search_objects.mapping.doc_type,
                id=content.id,
                body=special_coverage_filter,
            )
            # Translate perocolator results into SpecialCoverage objects
            if results["total"]:
                special_coverage_ids = [int(m["_id"].split(".")[-1]) for m in results["matches"]]
                qs = SpecialCoverage.objects.filter(id__in=special_coverage_ids)

                # Active Filter
                active = get_query_params(self.request).get('active', '').lower()
                now = timezone.now()
                if active == 'true':
                    qs = qs.filter(start_date__lte=now, end_date__gte=now)
                elif active == 'false':
                    qs = qs.exclude(start_date__lte=now, end_date__gte=now)

                # Sponsored Filter
                sponsored = get_query_params(self.request).get('sponsored', '').lower()
                if sponsored == 'true':
                    qs = qs.filter(tunic_campaign_id__isnull=False)
                elif sponsored == 'false':
                    qs = qs.exclude(tunic_campaign_id__isnull=False)

                serializer = SpecialCoverageSerializer(qs, many=True)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Http404('Must specify "content_id" param')


class CustomSearchContentViewSet(viewsets.GenericViewSet):
    """This is for searching with a custom search filter."""
    model = Content
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    paginate_by = 20
    permission_classes = [IsAdminUser, CanEditContent]
    field_map = {
        "feature-type": "feature_type.slug",
        "tag": "tags.slug",
        "content-type": "_type"
    }

    def list(self, request, *args, **kwargs):
        """Filter Content with a custom search.
        {
            "query": SEARCH_QUERY
            "preview": true
        }
        "preview" is optional and, when true, will include
        items that would normally be removed due to "excluded_ids".
        """

        queryset = self.get_filtered_queryset(get_request_data(request))
        # Switch between paginated or standard style responses
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """HACK: couldn't get POST to the list endpoint without
        messing up POST for the other list_routes so I'm doing this.
        Maybe something to do with the router?
        """
        return self.list(request, *args, **kwargs)

    def get_filtered_queryset(self, params, sort_pinned=True):
        query = params
        is_preview = params.get("preview", True)
        qs = custom_search_model(
            self.model, query, preview=is_preview,
            sort_pinned=sort_pinned, field_map=self.field_map
        )
        return qs.full()

    @list_route(methods=["get", "post"])
    def count(self, request, **kwargs):
        qs = self.get_filtered_queryset(get_request_data(request), sort_pinned=False)
        return Response(dict(count=qs.count()))

    @list_route(methods=["get", "post"])
    def group_count(self, request, **kwargs):
        params = dict(
            groups=[
                dict(get_request_data(request))
            ]
        )
        qs = self.get_filtered_queryset(params, sort_pinned=False)
        return Response(dict(count=qs.count()))


class SendContributorReport(viewsets.GenericViewSet):
    """Send contribution report email to all relevant ."""

    serializer_class = ContributorReportSerializer
    permission_classes = [IsAdminUser, CanEditContent]

    def create(self, request, *args, **kwargs):
        data = ContributorReportSerializer().to_internal_value(self.request.DATA)
        run_contributor_email_report.delay(**data)
        return Response(status=status.HTTP_200_OK)


# api router for aforementioned/defined viewsets
# note: me view is registered in urls.py
api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"content", ContentViewSet, base_name="content")
api_v1_router.register(r"custom-search-content", CustomSearchContentViewSet, base_name="custom-search-content")
api_v1_router.register(r"content-type", ContentTypeViewSet, base_name="content-type")
api_v1_router.register(r"content-resolve", ContentResolveViewSet, base_name="content-resolve")
api_v1_router.register(r"special-coverage-resolve", SpecialCoverageResolveViewSet, base_name="special-coverage-resolve")
api_v1_router.register(r"tag", TagViewSet, base_name="tag")
api_v1_router.register(r"log", LogEntryViewSet, base_name="logentry")
api_v1_router.register(r"author", AuthorViewSet, base_name="author")
api_v1_router.register(r"feature-type", FeatureTypeViewSet, base_name="feature-type")
api_v1_router.register(r"user", UserViewSet, base_name="user")
api_v1_router.register(r"contributor-email", SendContributorReport, base_name="contributor-email")
