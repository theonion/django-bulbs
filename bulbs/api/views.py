"""API Views and ViewSets"""

from django.conf import settings
from django.contrib.auth import get_user_model
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
