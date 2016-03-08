"""Logic for reading list behavior across all properties."""
from django.conf import settings
from django.core.cache import cache

from elasticsearch import TransportError
from elasticsearch_dsl import filter as es_filter

from bulbs.content.filters import NegateQueryFilter, SponsoredBoost
from bulbs.content.models import Content
from bulbs.content.search import randomize_es
from bulbs.sections.models import Section
from bulbs.special_coverage.models import SpecialCoverage
from .popular import get_popular_ids, popular_content
from .slicers import FirstSlotSlicer


READING_LIST_CONFIG = getattr(settings, "READING_LIST_CONFIG", {})


class ReadingListMixin(object):
    """Mixin for Content-based objects to manage reading lists."""

    def _get_reading_list_identifier(self):

        # 1. Match content to sponsored Special Coverages
        results = self.percolate_special_coverage(sponsored_only=True)
        if results:
            return results[0]

        # 2."Popular" i.e., the content is one of the 25 most popular items.
        popular_ids = get_popular_ids()
        if popular_ids and self.id in popular_ids:
            return "popular"

        # 3. Any unsponsored special coverage reading list that contains this item.
        results = self.percolate_special_coverage()
        if results:
            return results[0]

        # 4. Any section that contains this item.
        try:
            results = Content.search_objects.client.percolate(
                index=self.mapping.index,
                doc_type=self.mapping.doc_type,
                id=self.id,
                body={"filter": es_filter.Prefix(_id="section").to_dict()}
            )
        except TransportError:
            results = {"total": 0}

        if results["total"] > 0:
            for result in results["matches"]:
                if not result["_id"].endswith("None"):
                    return result["_id"]

        return "recent"

    def augment_reading_list(self, primary_query):
        """Apply injected logic for slicing reading lists with additional content."""
        primary_query = self.update_reading_list(primary_query)
        augment_query = self.update_reading_list(Content.search_objects.sponsored(
            excluded_ids=[self.id]
        ).filter(NegateQueryFilter(primary_query)))
        try:
            if not augment_query:
                return primary_query
            augment_query = randomize_es(augment_query)
            return FirstSlotSlicer(primary_query, augment_query)
        except TransportError:
            return primary_query

    def get_special_coverage_identifiers(self):
        cache_key = "special-coverage-identifiers-{}".format(self.id)
        identifiers = cache.get(cache_key)
        if identifiers is None:
            identifiers = self.percolate_special_coverage()
            cache.set(cache_key, identifiers, 60 * 5)
        return identifiers

    def get_reading_list_identifier(self):
        cache_key = "reading-list-identifier-{}".format(self.id)
        identifier = cache.get(cache_key)
        if identifier is None:
            identifier = self._get_reading_list_identifier()
            cache.set(cache_key, identifier, 60 * 5)
        return identifier

    def update_reading_list(self, reading_list):
        """Generic behaviors for reading lists before being rendered."""

        # remove the current piece of content from the query.
        reading_list = reading_list.filter(
            es_filter.Ids(values=[self.id])
        )

        # remove excluded document types from the query.
        excluded_doc_types = READING_LIST_CONFIG.get("excluded_doc_types", [])
        reading_list = reading_list.filter(
            ~es_filter.Types(values=excluded_doc_types)
        )

        return reading_list

    def get_reading_list_context(self):
        """Returns the context dictionary for a given reading list."""
        context = {
            "name": "",
            "content": None,
            "targeting": {},
            "videos": []
        }

        if self.reading_list_identifier == "popular":
            reading_list = popular_content()
            context.update({"name": self.reading_list_identifier})

        if self.reading_list_identifier.startswith("specialcoverage"):
            special_coverage = SpecialCoverage.objects.get_by_identifier(
                self.reading_list_identifier
            )
            reading_list = special_coverage.get_content().query(
                SponsoredBoost
            ).sort("_score", "-published")
            context.update({
                "name": special_coverage.name,
                "videos": special_coverage.videos,
                "targeting": {
                    "dfp_specialcoverage": special_coverage.slug
                },
            })
            if special_coverage.campaign:
                context["campaign"] = special_coverage.campaign
                context["targeting"].update({
                    "dfp_campaign": special_coverage.campaign.campaign_label,
                    "dfp_campaign_id": special_coverage.campaign.id
                })

        if self.reading_list_identifier.startswith("section"):
            section = Section.search_objects.get_by_identifier(self.reading_list_identifier)
            reading_list = section.get_content()
            context.update({"name": section.name})

        if not reading_list:
            reading_list = Content.search_objects.search()
            context.update({"name": "Recent News"})

        reading_list = self.augment_reading_list(reading_list)
        context.update({"content": reading_list})
        return context

    def get_reading_list(self, published=True):
        """
        This is currently a misnomer, as it actually returns a dictionary object.
        The returned object contains the reading list.
        """
        return self.get_reading_list_context(published=True)

    @property
    def reading_list_identifier(self):
        _reading_list_identifier = getattr(self, "_reading_list_identifier", None)
        if not _reading_list_identifier:
            setattr(self, "_reading_list_identifier", self.get_reading_list_identifier())
        return self._reading_list_identifier
