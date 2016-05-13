"""ElasticSearch filters specifially for content"""

import datetime
import dateutil.parser
import dateutil.tz
from django.utils import timezone

from elasticsearch_dsl.filter import Exists, MatchAll, Nested, Not, Range, Term, Terms
from elasticsearch_dsl.query import FunctionScore

from six import string_types, text_type, binary_type


def Evergreen(evergreen=True):
    return Term(evergreen=evergreen)


def parse_datetime(value):
    """Returns a datetime object for a given argument

    This helps to convert strings, dates and datetimes to proper tz-enabled
    datetime objects."""

    if isinstance(value, (string_types, text_type, binary_type)):
        value = dateutil.parser.parse(value)
        value.replace(tzinfo=dateutil.tz.tzutc())
        return value
    elif isinstance(value, datetime.datetime):
        value.replace(tzinfo=dateutil.tz.tzutc())
        return value
    elif isinstance(value, datetime.date):
        value = datetime.datetime(value.year, value.month, value.day)
        value.replace(tzinfo=dateutil.tz.tzutc())
        return value
    else:
        raise ValueError('Value must be parsable to datetime object. Got `{}`'.format(type(value)))


def _parse_slugs(slugs):
    included = []
    excluded = []
    for slug in slugs:
        if slug.startswith("-"):
            excluded.append(slug[1:])
        else:
            included.append(slug)

    return (included, excluded)


def Published(before=None, after=None):  # noqa
    published_params = {}
    if after is not None:
        published_params["gte"] = parse_datetime(after)

    if before is not None:
        published_params["lte"] = parse_datetime(before)

    if before is None and after is None:
        published_params["lte"] = timezone.now()

    return Range(published=published_params)


def Status(status):  # noqa
    if status:
        return Term(status=status)
    else:
        return MatchAll()


def Authors(usernames):  # noqa
    included, excluded = _parse_slugs(usernames)

    f = MatchAll()
    if included:
        f &= Terms(**{"authors.username": included})
    if excluded:
        f &= Terms(**{"authors.username": excluded})
    return f


def InstantArticle(active=True):  # noqa
    return Nested(path="feature_type", filter=Term(**{"feature_type.instant_article": active}))


def NegateQueryFilter(es_query):  # noqa
    """
    Return a filter removing the contents of the provided query.
    """
    query = es_query.to_dict().get("query", {})
    filtered = query.get("filtered", {})
    negated_filter = filtered.get("filter", {})
    return Not(**negated_filter)


def Tags(slugs):  # noqa
    included, excluded = _parse_slugs(slugs)

    f = MatchAll()
    if included:
        f &= Nested(path="tags", filter=Terms(**{"tags.slug": included}))
    if excluded:
        f &= ~Nested(path="tags", filter=Terms(**{"tags.slug": excluded}))

    return f


def FeatureTypes(slugs):  # noqa
    included, excluded = _parse_slugs(slugs)

    f = MatchAll()
    if included:
        f &= Nested(path="feature_type", filter=Terms(**{"feature_type.slug": included}))
    if excluded:
        f &= ~Nested(path="feature_type", filter=Terms(**{"feature_type.slug": excluded}))

    return f


def SponsoredBoost(field_name, boost_mode="multiply", weight=5):
    return FunctionScore(
        boost_mode=boost_mode,
        functions=[{
            "filter": Exists(field=field_name),
            "weight": weight
        }]
    )


def VideohubChannel(included_ids=None, excluded_ids=None):
    f = MatchAll()
    if included_ids:
        f &= Nested(path="video", filter=Terms(**{"video.channel_id": included_ids}))
    if excluded_ids:
        f &= ~Nested(path="video", filter=Terms(**{"video.channel_id": excluded_ids}))


def TagBoost(slugs, boost_mode="multiply", weight=5):
    included, excluded = _parse_slugs(slugs)
    return FunctionScore(
        boost_mode=boost_mode,
        functions=[{
            "filter": Nested(path="tags", filter=Terms(**{"tags.slug": included})),
            "weight": weight
        }]
    )


def FeatureTypeBoost(slugs, boost_mode="multiply", weight=5):
    included, excluded = _parse_slugs(slugs)
    return FunctionScore(
        boost_mode=boost_mode,
        functions=[{
            "filter": Nested(path="feature_type", filter=Terms(**{"feature_type.slug": included})),
            "weight": weight
        }]
    )
