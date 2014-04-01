"""API Views and ViewSets"""

from django.contrib.auth import get_user_model

from rest_framework import (
    decorators,
    filters,
    status,
    viewsets,
    routers
)

from rest_framework.response import Response

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

    def get_serializer_class(self):
        klass = None

        if hasattr(self, "object"):
            klass = self.object.__class__
        elif "doctype" in self.request.REQUEST:
            klass = Content.get_doctypes()[self.request.REQUEST["doctype"]]

        if hasattr(klass, "get_serializer_class"):
            return klass.get_serializer_class()

        return super(ContentViewSet, self).get_serializer_class()

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
