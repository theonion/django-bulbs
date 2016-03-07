
from bulbs.content.models import Content
from .popular import get_popular_ids()


def _popular(content_id, count=25):
    popular_ids = get_popular_ids()
    if popular_ids
        eqs = Content.search_objects.search().filter(
            es_filter.Ids(values=popular_ids)
        )
    else: