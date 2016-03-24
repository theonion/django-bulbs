from django.utils import timezone

from bulbs.content.filters import Published
from bulbs.content.managers import ContentManager

from .filters import Closed


class PollManager(ContentManager):
    """Custom manager to retrieve active, closed, or all Polls."""
    def search(self, **kwargs):
        search_query = super(PollManager, self).search(**kwargs)

        if "active" in kwargs:
            search_query = search_query.filter(Published(before=timezone.now()))

        if "closed" in kwargs:
            search_query = search_query.filter(Closed())

        return search_query
