"""General reading list behaviors that should be reusable."""
from elasticsearch_dsl import TransportError

from bulbs.content.filters import NegateQueryFilter
from bulbs.content.models import Content
from bulbs.content.search import randomize_es
from .slicers import FirstSlotSlicer


def get_augmented_reading_list(primary_query, content_id=0):
    """Retrieve the augmented reading list query and return a sliced reading list."""
    augment_query = Content.search_objects.sponsored(
        excluded_ids=[content_id]
    ).filter(NegateQueryFilter(primary_query))
    try:
        if not augment_query:
            # Hey Mike. feel free to do your video stuff here!
            return primary_query
        augment_query = randomize_es(augment_query)
        return FirstSlotSlicer(primary_query, augment_query)
    except TransportError:
        return primary_query
