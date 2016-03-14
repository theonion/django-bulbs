"""Custom search function to assist in customizing our special coverage searches."""
from elasticsearch_dsl import filter as es_filter

from bulbs.content.custom_search import get_condition_filter
from bulbs.content.models import Content
from bulbs.reading_list.slicers import SearchSlicer  # NOQA


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
