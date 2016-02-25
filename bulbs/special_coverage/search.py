"""Custom search function to assist in customizing our special coverage searches."""
from collections import OrderedDict

from django.conf import settings

from elasticsearch_dsl import filter as es_filter

from bulbs.content.custom_search import get_condition_filter
from bulbs.content.models import Content


class SearchParty(object):
    """Wrapper that searches for content from a group of SpecialCoverage objects."""

    def __init__(self, special_coverages):
        """Store list of special_coverages class level."""
        self._special_coverages = special_coverages
        self._query = {}

    def search(self):
        """Return a search using the combined query of all associated special coverage objects."""
        # Retrieve all Or filters pertinent to the special coverage query.
        should_filters = [
            es_filter.Terms(pk=self.query.get("included_ids", [])),
            es_filter.Terms(pk=self.query.get("pinned_ids", []))
        ]
        should_filters += self.get_group_filters()

        # Compile list of all Must filters.
        must_filters = [
            es_filter.Bool(should=should_filters),
            ~es_filter.Terms(pk=self.query.get("excluded_ids", []))
        ]

        return Content.search_objects.search().filter(es_filter.Bool(must=must_filters))

    def get_group_filters(self):
        """Return es OR filters to include all special coverage group conditions."""
        group_filters = []
        field_map = {
            "feature-type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        }
        for group_set in self.query.get("groups", []):
            for group in group_set:
                group_filter = es_filter.MatchAll()
                for condition in group.get("conditions", []):
                    group_filter &= get_condition_filter(condition, field_map=field_map)
                group_filters.append(group_filter)
        return group_filters

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
                self._query["excluded_ids"] += query.get("excluded_ids", [])
                self._query["included_ids"] += query.get("included_ids", [])
                self._query["pinned_ids"] += query.get("pinned_ids", [])
                self._query["groups"] += [query.get("groups", [])]
        return self._query


class SearchSlicer(object):
    """We want to search things like a seesaw. take that mike parent.
    """
    def __init__(self, *args, **kwargs):
        self.default_queryset = None
        self.querysets = OrderedDict()
        self.index = 0
        self.limit = kwargs.get("limit", getattr(settings, "READING_LIST_LIMIT", 100))

    def __iter__(self):
        return self

    def next(self):
        if self.index >= self.limit:
            raise StopIteration
        for validator, queryset in self.querysets.items():
            if validator(self.index):
                try:
                    result = queryset.next()
                    self.index += 1
                    return result
                except StopIteration:
                    pass
        result = self.default_queryset.next()
        self.index += 1
        return result

    def __next__(self):
        return self.next()

    def register_queryset(self, queryset, validator=None, default=False):
        """
        Add a given queryset to the iterator with custom logic for iteration.

        :param queryset: List of objects included in the reading list.
        :param validator: Custom logic to determine a queryset's position in a reading_list.
            Validators must accept an index as an argument and return a truthy value.
        :param default: Sets the given queryset as the primary queryset when no validator applies.
        """
        if default or self.default_queryset is None:
            self.default_queryset = queryset
            return
        if validator:
            self.querysets[validator] = queryset
        else:
            raise ValueError(
                """Querysets require validation logic to integrate with reading lists."""
            )
