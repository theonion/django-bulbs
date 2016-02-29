"""API filters for the Contribution App."""
from django.utils import dateparse, timezone

from rest_framework import filters

from bulbs.content.filters import Published


class ESPublishedFilterBackend(filters.BaseFilterBackend):
    """
    Used for elasticsearch publish queries in reporting.

    Rounds values to their given date & final second.
    """

    def filter_queryset(self, request, queryset, view):
        """Apply the relevant behaviors to the view queryset."""
        start_value = self.get_date_datetime_param(request, "start")
        if start_value:
            queryset = self.apply_published_filter(queryset, "after", start_value)
        end_value = self.get_date_datetime_param(request, "end")
        if end_value:
            # Forces the end_value to be the last second of the date provided in the query.
            # Necessary currently as our Published filter for es only applies to gte & lte.
            end_value += timezone.timedelta(days=1)
            end_value = (
                timezone.datetime.combine(end_value, timezone.datetime.min.time()) -
                timezone.timedelta(seconds=1)
            )
            queryset = self.apply_published_filter(queryset, "before", end_value)
        return queryset

    def apply_published_filter(self, queryset, operation, value):
        """
        Add the appropriate Published filter to a given elasticsearch query.

        :param queryset: The DJES queryset object to be filtered.
        :param operation: The type of filter (before/after).
        :param value: The date or datetime value being applied to the filter.
        """
        if operation not in ["after", "before"]:
            raise ValueError("""Publish filters only use before or after for range filters.""")
        return queryset.filter(Published(**{operation: value}))

    def get_date_datetime_param(self, request, param):
        """Check the request for the provided query parameter and returns a rounded value.

        :param request: WSGI request object to retrieve query parameter data.
        :param param: the name of the query parameter.
        """
        if param in request.GET:
            param_value = request.GET.get(param, None)
            # Match and interpret param if formatted as a date.
            date_match = dateparse.date_re.match(param_value)
            if date_match:
                return dateparse.parse_date(date_match.group(0))
            datetime_match = dateparse.datetime_re.match(param_value)
            if datetime_match:
                return dateparse.parse_datetime(datetime_match.group(0)).date()
        return None


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
