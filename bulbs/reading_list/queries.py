from elasticsearch_dsl import filter as es_filter

from bulbs.content.models import Content
from .popular import get_popular_ids, DEFAULT_LIMIT


def popular_content(**kwargs):
    """
    Use the get_popular_ids() to retrieve trending content objects.
    Return recent content on failure.
    """
    limit = kwargs.get("limit", DEFAULT_LIMIT)
    popular_ids = get_popular_ids(limit=limit)
    if not popular_ids:
        return recent_content()
    return Content.search_objects.search().filter(es_filter.Ids(values=popular_ids))


def recent_content():
    """Useless for now, but all logic relevant to logic should be applied here."""
    return Content.search_objects.search()
