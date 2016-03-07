from requests import ConnectionError

from django.conf import settings

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
