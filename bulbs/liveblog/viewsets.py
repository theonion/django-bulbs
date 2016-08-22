from rest_framework import filters, viewsets
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.permissions import AllowAny, IsAdminUser

from bulbs.api.permissions import CanEditContent
from .filters import IfModifiedSinceFilterBackend, LiveBlogFilterBackend
from .models import LiveBlogEntry
from .serializers import LiveBlogEntrySerializer


class LiveBlogEntryViewSet(viewsets.ModelViewSet):

    queryset = LiveBlogEntry.objects.all()
    # model = LiveBlogEntry
    serializer_class = LiveBlogEntrySerializer
    permission_classes = [IsAdminUser, CanEditContent]
    filter_backends = (
        filters.OrderingFilter,
        LiveBlogFilterBackend,
    )
    ordering_fields = (
        "published",
    )

    # Avoid immediate need for FE pagination
    paginate_by = 500


class PublicLiveBlogEntryViewSet(CacheResponseMixin, LiveBlogEntryViewSet):

    permission_classes = (AllowAny,)
    filter_backends = (
        filters.OrderingFilter,
        IfModifiedSinceFilterBackend,
        LiveBlogFilterBackend,
    )
