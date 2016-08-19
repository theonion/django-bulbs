from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from bulbs.api.permissions import CanEditContent
from .filters import IfModifiedSinceFilterBackend
from .models import LiveBlogEntry
from .serializers import LiveBlogEntrySerializer


class LiveBlogEntryViewSet(viewsets.ModelViewSet):

    queryset = LiveBlogEntry.objects.all()
    # model = LiveBlogEntry
    serializer_class = LiveBlogEntrySerializer
    permission_classes = [IsAdminUser, CanEditContent]
    filter_backends = (
        filters.OrderingFilter,
        IfModifiedSinceFilterBackend,
    )
    ordering_fields = (
        "published",
    )

    # Avoid immediate need for FE pagination
    paginate_by = 500
