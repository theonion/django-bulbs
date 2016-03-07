from requests import ConnectionError

from django.conf import settings

from elasticsearch_dsl import filter as es_filter
from pageview_client.clients import TrendingClient

from bulbs.content.models import Content


DEFAULT_LIMIT = 10


trending_client = TrendingClient(settings.DIGEST_HOSTNAME, settings.DIGEST_ENDPOINT)


def get_popular_ids(limit=DEFAULT_LIMIT):
    try:
        ids = trending_client.get(settings.DIGEST_SITE, offset=settings.DIGEST_OFFSET, limit=limit)
        return list(ids)[:limit]
    except ConnectionError:
        return None


def popular_content(**kwargs):
    """
    Use the get_popular_ids() to retrieve trending content objects.
    Return recent content on failure.
    """
    limit = kwargs.get("limit", DEFAULT_LIMIT)
    popular_ids = get_popular_ids(limit=limit)
    if not popular_ids:
        # Return most recent content
        return Content.search_objects.search().extra(size=limit)
    return Content.search_objects.search().filter(es_filter.Ids(values=popular_ids))
