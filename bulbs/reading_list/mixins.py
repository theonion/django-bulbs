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

    def validate_query(self, query):
        """Confirm query exists given common filters."""
        if query is None:
            return query
        query = self.update_reading_list(query)
        return query

    def get_validated_augment_query(self, augment_query=None):
        """
        Common rules for reading list augmentation hierarchy.

        1. Sponsored Content.
        2. Video Content.
        """
        augment_query = self.validate_query(augment_query)

        # Given an invalid query, reach for a Sponsored query.
        if not augment_query:
            augment_query = self.validate_query(Content.search_objects.sponsored())

        # Given an invalid Sponsored query, reach for a Video query.
        if not augment_query:
            reading_list_config = getattr(settings, "READING_LIST_CONFIG", {})
            excluded_channel_ids = reading_list_config.get("excluded_channel_ids", [])
            augment_query = self.validate_query(Content.search_objects.evergreen_video(
                excluded_channel_ids=excluded_channel_ids
            ))

        return augment_query

    def augment_reading_list(self, primary_query, augment_query=None, reverse_negate=False):
        """Apply injected logic for slicing reading lists with additional content."""
        primary_query = self.validate_query(primary_query)
        augment_query = self.get_validated_augment_query(augment_query=augment_query)

        try:
            # We use this for cases like recent where queries are vague.
            if reverse_negate:
                primary_query = primary_query.filter(NegateQueryFilter(augment_query))
            else:
                augment_query = augment_query.filter(NegateQueryFilter(primary_query))
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
            ~es_filter.Ids(values=[self.id])
        )

        # remove excluded document types from the query.
        reading_list_config = getattr(settings, "READING_LIST_CONFIG", {})
        excluded_doc_types = reading_list_config.get("excluded_doc_types", [])
        for obj in excluded_doc_types:
            reading_list = reading_list.filter(~es_filter.Type(value=obj))

        return reading_list

    def get_reading_list_context(self):
        """Returns the context dictionary for a given reading list."""
        reading_list = None
        context = {
            "name": "",
            "content": reading_list,
            "targeting": {},
            "videos": []
        }

        if self.reading_list_identifier == "popular":
            reading_list = popular_content()
            context.update({"name": self.reading_list_identifier})

            # Popular is augmented.
            reading_list = self.augment_reading_list(reading_list)
            context.update({"content": reading_list})
            return context

        if self.reading_list_identifier.startswith("specialcoverage"):
            special_coverage = SpecialCoverage.objects.get_by_identifier(
                self.reading_list_identifier
            )
            reading_list = special_coverage.get_content().query(
                SponsoredBoost(field_name="tunic_campaign_id")
            ).sort("_score", "-published")
            context["targeting"]["dfp_specialcoverage"] = special_coverage.slug
            if special_coverage.tunic_campaign_id:
                context["tunic_campaign_id"] = special_coverage.tunic_campaign_id
                context["targeting"].update({
                    "dfp_campaign_id": special_coverage.tunic_campaign_id
                })
                # We do not augment sponsored special coverage lists.
                reading_list = self.update_reading_list(reading_list)
            else:
                reading_list = self.augment_reading_list(reading_list)
            context.update({
                "name": special_coverage.name,
                "videos": special_coverage.videos,
                "content": reading_list
            })
            return context

        if self.reading_list_identifier.startswith("section"):
            section = Section.objects.get_by_identifier(self.reading_list_identifier)
            reading_list = section.get_content()
            reading_list = self.augment_reading_list(reading_list)
            context.update({
                "name": section.name,
                "content": reading_list
            })
            return context

        reading_list = Content.search_objects.search()
        reading_list = self.augment_reading_list(reading_list, reverse_negate=True)
        context.update({
            "name": "Recent News",
            "content": reading_list
        })
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
