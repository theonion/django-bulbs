from rest_framework import filters, viewsets
# from rest_framework.permissions import IsAdminUser

# from bulbs.api.permissions lmport CanEditContent
from .filters import IfModifiedSinceFilterBackend
from .models import LiveBlogEntry
from .serializers import LiveBlogEntrySerializer


class LiveBlogEntryViewSet(viewsets.ModelViewSet):

    model = LiveBlogEntry
    queryset = LiveBlogEntry.objects.all()  # TODO: filter(parent__isnull=True)
    # TODO: Necessary?
    serializer_class = LiveBlogEntrySerializer
    # permission_classes = [IsAdminUser, CanEditContent]  # TODO: ??

    filter_backends = (
        filters.OrderingFilter,
        IfModifiedSinceFilterBackend,
    )
    ordering_fields = (
        "published",
    )
    # filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    # search_fields = ("title",)
    # ordering_fields = ("title",)

    # Avoid immediate need for FE pagination
    paginate_by = 500
