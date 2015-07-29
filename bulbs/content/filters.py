"""ElasticSearch filters specifially for content"""

import datetime
import dateutil.parser
import dateutil.tz
from django.utils import timezone
from elasticsearch_dsl.filter import Term, Terms, Range, MatchAll, Nested
from six import string_types, text_type, binary_type


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
    included = []
    excluded = []
    for username in usernames:
        if username.startswith("-"):
            excluded.append(username[1:])
        else:
            included.append(username)
    f = MatchAll()
    if included:
        f &= Terms(**{"authors.username": included})
    if excluded:
        f &= Terms(**{"authors.username": excluded})
    return f


def Tags(slugs):  # noqa
    included = []
    excluded = []
    for slug in slugs:
        if slug.startswith("-"):
            excluded.append(slug[1:])
        else:
            included.append(slug)

    f = MatchAll()
    if included:
        f &= Nested(path="tags", filter=Terms(**{"tags.slug": included}))
    if excluded:
        f &= ~Nested(path="tags", filter=Terms(**{"tags.slug": excluded}))

    return f


def FeatureTypes(slugs):  # noqa
    included = []
    excluded = []
    for slug in slugs:
        if slug.startswith("-"):
            excluded.append(slug[1:])
        else:
            included.append(slug)

    f = MatchAll()
    if included:
        f &= Nested(path="feature_type", filter=Terms(**{"feature_type.slug": included}))
    if excluded:
        f &= ~Nested(path="feature_type", filter=Terms(**{"feature_type.slug": excluded}))

    return f
