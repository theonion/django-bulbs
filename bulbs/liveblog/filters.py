from rest_framework import filters


logger = __import__('logging').getLogger(__name__)


class LiveBlogFilterBackend(filters.BaseFilterBackend):
    """
    Optionally include only entries belonging to specified LiveBlog.
    """
    def filter_queryset(self, request, queryset, view):
        liveblog_id = request.GET.get('liveblog')
        if liveblog_id:
            queryset = queryset.filter(liveblog_id=liveblog_id)

        return queryset
