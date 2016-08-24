from rest_framework import filters
from rest_framework.exceptions import ParseError

from django.utils import dateparse


logger = __import__('logging').getLogger(__name__)


class IfModifiedSinceFilterBackend(filters.BaseFilterBackend):
    """
    Optionally exclude older requests.

    Expects ISO 8601-formatted "if_modified_since" query param.
    """
    def filter_queryset(self, request, queryset, view):
        if_modified_since = request.GET.get('if_modified_since')
        if if_modified_since:
            when = dateparse.parse_datetime(if_modified_since)
            if when:
                return queryset.filter(published__gt=when)
            else:
                raise ParseError('Bad "if_modified_since" date: {}'.format(if_modified_since))
        else:
            return queryset


class LiveBlogFilterBackend(filters.BaseFilterBackend):
    """
    Optionally include only entries belonging to specified LiveBlog.
    """
    def filter_queryset(self, request, queryset, view):
        liveblog_id = request.GET.get('liveblog_id')
        if liveblog_id:
            queryset = queryset.filter(liveblog_id=liveblog_id)

        return queryset
