"""Generic manager for all indexable content and common queries."""
from django.conf import settings
from django.utils import timezone

from djes.models import IndexableManager
from elasticsearch_dsl import filter as es_filter
from polymorphic import PolymorphicManager

from .filters import (
    Authors, Evergreen, FeatureTypes, InstantArticle, Published, Status, Tags,
    VideohubChannel
)


class ContentManager(PolymorphicManager, IndexableManager):
    """a specialized version of `djes.models.SearchManager` for `bulbs.content.Content`."""

    def evergreen(self, included_channel_ids=None, excluded_channel_ids=None, **kwargs):
        """
        Search containing any evergreen piece of Content.

        :included_channel_ids list: Contains ids for channel ids relevant to the query.
        :excluded_channel_ids list: Contains ids for channel ids excluded from the query.
        """
        eqs = self.search(**kwargs)
        eqs = eqs.filter(Evergreen())
        if included_channel_ids:
            eqs = eqs.filter(VideohubChannel(included_ids=included_channel_ids))
        if excluded_channel_ids:
            eqs = eqs.filter(VideohubChannel(excluded_ids=excluded_channel_ids))
        return eqs

    def evergreen_video(self, **kwargs):
        """Filter evergreen content to exclusively video content."""
        eqs = self.evergreen(**kwargs)
        video_doc_type = getattr(settings, "VIDEO_DOC_TYPE", "")
        eqs = eqs.filter(es_filter.Type(value=video_doc_type))
        return eqs

    def instant_articles(self, **kwargs):
        """
        QuerySet including all published content approved for instant articles.

        Instant articles are configured via FeatureType. FeatureType.instant_article = True.
        """
        eqs = self.search(**kwargs).sort('-last_modified', '-published')
        return eqs.filter(InstantArticle())

    def sponsored(self, **kwargs):
        """Search containing any sponsored pieces of Content."""
        eqs = self.search(**kwargs)
        eqs = eqs.filter(es_filter.Exists(field="tunic_campaign_id"))
        published_offset = getattr(settings, "RECENT_SPONSORED_OFFSET_HOURS", None)
        if published_offset:
            now = timezone.now()
            eqs = eqs.filter(
                Published(
                    after=now - timezone.timedelta(hours=published_offset),
                    before=now
                )
            )
        return eqs

    def search(self, **kwargs):
        """
        Query using ElasticSearch, returning an elasticsearch queryset.

        :param kwargs: keyword arguments (optional)
         * query : ES Query spec
         * tags : content tags
         * types : content types
         * feature_types : featured types
         * published : date range
        """
        search_query = super(ContentManager, self).search()

        if "query" in kwargs:
            search_query = search_query.query("match", _all=kwargs.get("query"))
        else:
            search_query = search_query.sort('-published', '-last_modified')

        # Right now we have "Before", "After" (datetimes),
        # and "published" (a boolean). Should simplify this in the future.
        if "before" in kwargs or "after" in kwargs:
            published_filter = Published(before=kwargs.get("before"), after=kwargs.get("after"))
            search_query = search_query.filter(published_filter)
        else:
            # TODO: kill this "published" param. it sucks
            if kwargs.get("published", True) and "status" not in kwargs:
                published_filter = Published()
                search_query = search_query.filter(published_filter)

        if "status" in kwargs:
            search_query = search_query.filter(Status(kwargs["status"]))

        if "excluded_ids" in kwargs:
            exclusion_filter = ~es_filter.Ids(values=kwargs.get("excluded_ids", []))
            search_query = search_query.filter(exclusion_filter)

        tag_filter = Tags(kwargs.get("tags", []))
        search_query = search_query.filter(tag_filter)

        author_filter = Authors(kwargs.get("authors", []))
        search_query = search_query.filter(author_filter)

        feature_type_filter = FeatureTypes(kwargs.get("feature_types", []))
        search_query = search_query.filter(feature_type_filter)

        # Is this good enough? Are we even using this feature at all?
        types = kwargs.pop("types", [])
        if types:
            search_query._doc_type = types
        return search_query
