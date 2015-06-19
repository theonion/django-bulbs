from rest_framework import filters


class CaseInsensitiveBooleanFilter(filters.BaseFilterBackend):
    """Set a boolean_fields tuple on the viewset and set this class as a
    filter_backend to filter listed fields through a case-insensitive transformation
    to be used for filtering. i.e. query params such as 'true' become boolean
    True, and params with a value 'false' become boolean False."""

    def filter_queryset(self, request, queryset, view):

        boolean_fields = getattr(view, 'boolean_fields', None)

        if not boolean_fields:
            return queryset

        boolean_filters = {}
        for field in boolean_fields:
            if field in request.QUERY_PARAMS:
                val = request.QUERY_PARAMS[field].lower()
                if val == 'true':
                    boolean_filters[field] = True
                elif val == 'false':
                    boolean_filters[field] = False

        if len(boolean_filters) > 0:
            return queryset.filter(**boolean_filters)

        return queryset
