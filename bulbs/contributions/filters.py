from django.utils import dateparse

from rest_framework import filters


class StartEndFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        start = request.QUERY_PARAMS.get("start", None)
        if start:
            start_date = dateparse.parse_date(start)
            queryset = self.filter_start(queryset, view, start_date)
        end = request.QUERY_PARAMS.get("end", None)
        if end:
            end_date = dateparse.parse_date(end)
            queryset = self.filter_end(queryset, view, end_date)
        return queryset

    def filter_start(self, queryset, view, start_date):
        start_fields = getattr(view, "start_fields", None)
        if start_fields:
            _filters = {}
            for field_name in start_fields:
                _filters = {"{}__gte".format(field_name): start_date}
        return queryset.filter(**_filters)

    def filter_end(self, queryset, view, end_date):
        end_fields = getattr(view, "end_fields", None)
        if end_fields:
            _filters = {}
            for field_name in end_fields:
                _filters = {"{}__lte".format(field_name): end_date}
        return queryset.filter(**_filters)
