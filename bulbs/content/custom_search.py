"""Custom ES filter builder

    Query format:
    {
        groups: [
            {
                conditions: [
                    field: "es.field.name",
                    type: <"all"|"any"|"none">,
                    values: [
                        {
                            label: "For humans",
                            value: "for-the-computers"
                        },
                        ...
                    ]
                ],
                time: 'X days'
            },
            ...
        ],
        included_ids: [],
        excluded_ids: [],
        pinned_ids: []
    }
    bool(groups) = bool(group0) OR ... OR bool(groupN)
    bool(group) = bool(field0, op0, values0) AND ... AND bool(fieldN, opN, valuesN)
    bool(field, "all", values) = field contains all of these values
    bool(field, "any", values) = field contains at least one of these values
    bool(field, "none", values) = field contains none of these values
"""
from datetime import timedelta

from django.utils import timezone
from elasticutils import F

from bulbs.conf import settings


def custom_search_model(model, query, preview=False, published=False,
                        id_field="id", time_field="published", sort_pinned=True, field_map={}):
    """Filter a model with the given filter.

    `field_map` translates incoming field names to the appropriate ES names.
    """
    if preview:
        func = preview_filter_from_query
    else:
        func = filter_from_query
    f = func(query, id_field=id_field, time_field=time_field, field_map=field_map)
    # filter by published
    if published:
        now = timezone.now()
        f &= F(**{time_field + "__lte": now})
    qs = model.search_objects.s().filter(f)
    # possibly include a text query
    if query.get("query"):
        qs = qs.query(_all__match=query["query"], must=True)
    # set up pinned ids
    pinned_ids = query.get("pinned_ids")
    if pinned_ids and sort_pinned:
        #
        # PLEASE UPGRADE ME!
        #
        # ElasticUtils doesn't provide hooks to scoring functions (other than boost/demote).
        # This is a workaround to prioritize Pinned IDs without using query_raw().
        #
        # Original implemntation used a function_score via a query_raw() call. This worked, but
        # query_raw() causes all query() calls to be ignored, so it was not possible to chain
        # additional query() calls to the result (see previous Git revision).
        #
        # The workaround is to use demote() to lower the scores for pinned IDs, and then sort by low
        # score. (Couldn't get query+boost to work with ID list).
        #
        # The real solution is to upgrade away from elasticutils.

        # First we begin with a HACK: Need to ensure there is at least one positive query for
        # demote() to work.
        # Workaround is to just do an "always true" query like ID >= 0. Might be able to just check
        # if qs.build_search() is False/empty, but this is a workaround anyway and should be
        # replaced entirely.
        qs = qs.query(id__gte=0)
        # Demote will penalize Pinned ID results, and then we'll sort by lowest score first.
        qs = qs.demote(2, id__in=pinned_ids)
        qs = qs.order_by("_score", "-published")
    else:
        qs = qs.order_by("-published")
    return qs


def preview_filter_from_query(query, id_field="id", time_field="published", field_map={}):
    """This filter includes the "excluded_ids" so they still show up in the editor."""
    f = groups_filter_from_query(query, time_field=time_field, field_map=field_map)
    # NOTE: we don't exclude the excluded ids here so they show up in the editor
    # include these, please
    included_ids = query.get("included_ids")
    if included_ids:
        f |= F(**{id_field + "__in": included_ids})
    return f


def filter_from_query(query, id_field="id", time_field="published", field_map={}):
    """This returns a filter which actually filters out everything, unlike the
    preview filter which includes excluded_ids for UI purposes.
    """
    f = groups_filter_from_query(query, time_field=time_field, field_map=field_map)
    excluded_ids = query.get("excluded_ids")
    included_ids = query.get("included_ids")
    if excluded_ids:  # exclude these
        f &= ~F(**{id_field + "__in": excluded_ids})
    if included_ids:  # include these, please
        f |= F(**{id_field + "__in": included_ids})
    return f


def groups_filter_from_query(query, time_field="published", field_map={}):
    """Creates an F object for the groups of a search query."""
    f = F()
    # filter groups
    for group in query.get("groups", []):
        group_f = F()
        for condition in group.get("conditions", []):
            field_name = condition["field"]
            field_name = field_map.get(field_name, field_name)
            operation = condition["type"]
            values = condition["values"]
            if values:
                values = [v["value"] for v in values]
                if operation == "all":
                    # NOTE: is there a better way to express this?
                    for value in values:
                        group_f &= F(**{field_name: value})
                elif operation == "any":
                    group_f &= F(**{field_name + "__in": values})
                elif operation == "none":
                    group_f &= ~F(**{field_name + "__in": values})
        date_range = group.get("time")
        if date_range:
            group_f &= date_range_filter(date_range, time_field)
        f |= group_f
    return f


def date_range_filter(range_name, field_name):
    """Create a filter from a named date range."""

    filter_days = filter(
        lambda time: time["label"] == range_name,
        settings.CUSTOM_SEARCH_TIME_PERIODS)
    num_days = filter_days[0]["days"] if len(filter_days) else None

    if num_days:
        dt = timedelta(num_days)
        start_time = timezone.now() - dt
        return F(**{field_name + "__gte": start_time})
    return F()
