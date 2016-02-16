"""Custom search function to assist in customizing our special coverage searches."""
import six


class SearchParty(object):
    """Wrapper that searches for content from a group of SpecialCoverage objects."""

    _query = {}

    def __init__(self, special_coverages, *args, **kwargs):
        """Store list of special_coverages class level."""
        self._special_coverages = special_coverages

    @property
    def query(self):
        """Group the self.special_coverages queries and memoize them."""
        if not self._query:
            self._query.update({
                "excluded_ids": [],
                "included_ids": [],
                "pinned_ids": [],
                "groups": [],
            })
            for special_coverage in self._special_coverages:
                # Access query at dict level.
                query = getattr(special_coverage, "query", {})
                if "query" in query:
                    query = query.get("query")

                self._query.update({

                })
                self._query["excluded_ids"] += query.get("excluded_ids", [])
                self._query["included_ids"] += query.get("included_ids", [])
                self._query["pinned_ids"] += query.get("pinned_ids", [])
                self._query["groups"] += query.get("groups", [])
        return self._query


def second_slot_query_generator(query1, query2):
    """Returns the result of a different query at the 1st index of iteration.

    :param query1: Primary search that will be the default result set.
    :type  query1: Any iterable object; intended for djes.search.LazySearch and django.Querysets.
    :param query2: Secondard search that will return at the 1st index of iteration.
    :type  query2: Any iterable object; intended for djes.search.LazySearch and django.Querysets.
    """
    index = 0
    while True:
        result = None
        if index == 1:
            try:
                result = six.next(query2)
            except IndexError:
                pass
        if result is None:
            try:
                result = six.next(query1)
            except IndexError:
                break
        yield result
        index += 1
