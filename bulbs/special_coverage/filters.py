from django.utils import timezone

from bulbs.utils.filters import CaseInsensitiveBooleanFilter
from bulbs.utils.methods import get_query_params


class SpecialCoverageFilter(CaseInsensitiveBooleanFilter):
    """
    Includes the default boolean_filter, but replaces the active and inactive states to represent
    whether the current_date is within a SpecialCoverage's start_date & end_date range.
    """
    def filter_queryset(self, request, queryset, view):
        queryset = super(SpecialCoverageFilter, self).filter_queryset(request, queryset, view)
        query_params = get_query_params(request)
        if "active" in query_params:
            today_filter = timezone.now()
            value = query_params.get("active").lower()
            if value == "true":
                queryset = queryset.filter(
                    start_date__lte=today_filter, end_date__gte=today_filter
                )
            elif value == "false":
                queryset == queryset.exclude(
                    start_date__lte=today_filter, end_date__gte=today_filter
                )
        return queryset
