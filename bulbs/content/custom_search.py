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
from elasticsearch_dsl.filter import Term, Terms, MatchAll, Nested, Range
from elasticsearch_dsl import query as es_query

from bulbs.conf import settings


def custom_search_model(model, query, preview=False, published=False,
                        id_field="id", sort_pinned=True, field_map={}):
    """Filter a model with the given filter.

    `field_map` translates incoming field names to the appropriate ES names.
    """
    if preview:
        func = preview_filter_from_query
    else:
        func = filter_from_query
    f = func(query, id_field=id_field, field_map=field_map)
    # filter by published
    if published:
        if f:
            f &= Range(published={"lte": timezone.now()})
        else:
            f = Range(published={"lte": timezone.now()})

    qs = model.search_objects.search(published=False)
    if f:
        qs = qs.filter(f)

    # possibly include a text query
    if query.get("query"):
        qs = qs.query("match", _all=query["query"])
    # set up pinned ids
    pinned_ids = query.get("pinned_ids")
    if pinned_ids and sort_pinned:

        pinned_query = es_query.FunctionScore(
            boost_mode="multiply",
            functions=[{
                "filter": Terms(id=pinned_ids),
                "weight": 2
            }]
        )

        qs = qs.query(pinned_query)
        qs = qs.sort("_score", "-published")
    else:
        qs = qs.sort("-published")
    return qs


def preview_filter_from_query(query, id_field="id", field_map={}):
    """This filter includes the "excluded_ids" so they still show up in the editor."""
    f = groups_filter_from_query(query, field_map=field_map)
    # NOTE: we don't exclude the excluded ids here so they show up in the editor
    # include these, please
    included_ids = query.get("included_ids")
    if included_ids:
        if f:
            f |= Terms(pk=included_ids)
        else:
            f = Terms(pk=included_ids)
    return f


def filter_from_query(query, id_field="id", field_map={}):
    """This returns a filter which actually filters out everything, unlike the
    preview filter which includes excluded_ids for UI purposes.
    """
    f = groups_filter_from_query(query, field_map=field_map)
    excluded_ids = query.get("excluded_ids")
    included_ids = query.get("included_ids")

    if included_ids:  # include these, please
        if f is None:
            f = Terms(pk=included_ids)
        else:
            f |= Terms(pk=included_ids)

    if excluded_ids:  # exclude these
        if f is None:
            f = MatchAll()

        f &= ~Terms(pk=excluded_ids)
    return f


def groups_filter_from_query(query, field_map={}):
    """Creates an F object for the groups of a search query."""
    f = None
    # filter groups
    for group in query.get("groups", []):
        group_f = MatchAll()
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
                        if "." in field_name:
                            path = field_name.split(".")[0]
                            group_f &= Nested(path=path, filter=Term(**{field_name: value}))
                        else:
                            group_f &= Term(**{field_name: value})
                elif operation == "any":
                    if "." in field_name:
                        path = field_name.split(".")[0]
                        group_f &= Nested(path=path, filter=Terms(**{field_name: values}))
                    else:
                        group_f &= Terms(**{field_name: values})
                elif operation == "none":
                    if "." in field_name:
                        path = field_name.split(".")[0]
                        group_f &= ~Nested(path=path, filter=Terms(**{field_name: values}))
                    else:
                        group_f &= ~Terms(**{field_name: values})

        date_range = group.get("time")
        if date_range:
            group_f &= date_range_filter(date_range)
        if f:
            f |= group_f
        else:
            f = group_f
    return f


def date_range_filter(range_name):
    """Create a filter from a named date range."""

    filter_days = list(filter(
        lambda time: time["label"] == range_name,
        settings.CUSTOM_SEARCH_TIME_PERIODS))
    num_days = filter_days[0]["days"] if len(filter_days) else None

    if num_days:
        dt = timedelta(num_days)
        start_time = timezone.now() - dt
        return Range(published={"gte": start_time})
    return MatchAll()
