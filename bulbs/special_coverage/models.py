from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.db import models
from django.template.defaultfilters import slugify

from elasticsearch import Elasticsearch
from json_field import JSONField

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content
from bulbs.content.mixins import DetailImageMixin
from bulbs.utils.methods import (datetime_to_epoch_seconds,
                                 today_as_utc_datetime,
                                 is_valid_digit)
from .managers import SpecialCoverageManager


es = Elasticsearch(settings.ES_CONNECTIONS["default"]["hosts"])


class SpecialCoverage(DetailImageMixin, models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    query = JSONField(default={}, blank=True)
    videos = JSONField(default=[], blank=True)
    active = models.BooleanField(default=False)
    promoted = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    # Tunic Campaign ID
    # NOTE: Don't want to accidentally overwrite derived model campaign_id fields during migration
    # Will rename to "campaign_id" (and drop "campaign" field) after migration
    tunic_campaign_id = models.IntegerField(blank=True, null=True, default=None)
    # Property-specific custom configuration
    config = JSONField(default={}, blank=True)

    objects = SpecialCoverageManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        super(SpecialCoverage, self).clean()
        self.clean_publish_dates()
        self.clean_query()
        self.clean_videos()

    def clean_publish_dates(self):
        """
        If an end_date value is provided, the start_date must be less.
        """
        if self.end_date:
            if not self.start_date:
                raise ValidationError("""The End Date requires a Start Date value.""")
            elif self.end_date <= self.start_date:
                raise ValidationError("""The End Date must not precede the Start Date.""")
        if self.start_date and not self.end_date:
            raise ValidationError("""The Start Date requires an End Date.""")

    def clean_query(self):
        """
        Removes any `None` value from an elasticsearch query.
        """
        if self.query and self.query != {}:
            for key, value in self.query.items():
                if isinstance(value, list) and None in value:
                    self.query[key] = [v for v in value if v is not None]

    def clean_videos(self):
        """
        Validates that all values in the video list are integer ids and removes all None values.
        """
        if self.videos:
            self.videos = [int(v) for v in self.videos if v is not None and is_valid_digit(v)]

    def save(self, *args, **kwargs):
        """Saving ensures that the slug, if not set, is set to the slugified name."""
        self.clean()

        if not self.slug:
            self.slug = slugify(self.name)

        super(SpecialCoverage, self).save(*args, **kwargs)

        if self.query and self.query != {}:
            # Always save and require client to filter active date range
            self._save_percolator()

    def _save_percolator(self):
        """
        Saves the query field as an elasticsearch percolator
        """
        index = Content.search_objects.mapping.index
        query_filter = self.get_content(published=False).to_dict()

        q = {}

        if "query" in query_filter:
            q = {"query": query_filter.get("query", {})}
        else:
            # We don't know how to save this
            return

        # We'll need this data, to decide which special coverage section to use
        q["sponsored"] = bool(self.tunic_campaign_id)
        # Elasticsearch v1.4 percolator "field_value_factor" does not
        # support missing fields, so always need to include

        q["start_date"] = self.start_date
        q["end_date"] = self.end_date

        # Elasticsearch v1.4 percolator range query does not support DateTime range queries
        # (PercolateContext.nowInMillisImpl is not implemented).
        if q["start_date"]:
            q['start_date_epoch'] = datetime_to_epoch_seconds(q["start_date"])
        if q["end_date"]:
            q['end_date_epoch'] = datetime_to_epoch_seconds(q["end_date"])

        # Store manually included IDs for percolator retrieval scoring (boost
        # manually included content).
        if self.query:
            q['included_ids'] = self.query.get('included_ids', [])

        es.index(
            index=index,
            doc_type=".percolator",
            body=q,
            id=self.es_id
        )

    def _delete_percolator(self):
        index = Content.search_objects.mapping.index
        es.delete(index=index, doc_type=".percolator", id=self.es_id, refresh=True, ignore=404)

    def get_content(self, published=True):
        """performs es search and gets content objects
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        search = custom_search_model(Content, q, published=published, field_map={
            "feature-type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        })
        return search

    @property
    def is_active(self):
        now = today_as_utc_datetime()
        if self.start_date and self.end_date:
            return self.start_date <= now < self.end_date
        return False

    @property
    def es_id(self):
        return "specialcoverage.{}".format(self.id)

    @property
    def contents(self):
        """performs .get_content() and caches it in a ._content property
        """
        if not hasattr(self, "_content"):
            self._content = self.get_content()
        return self._content

    @property
    def identifier(self):
        return "specialcoverage.{}".format(self.id)

    @property
    def has_pinned_content(self):
        """determines if the there is a pinned object in the search
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        if "pinned_ids" in q:
            return bool(len(q.get("pinned_ids", [])))
        return False

    @property
    def custom_template_name(self):
        """
        Returns the path for the custom special coverage template we want.
        """
        base_path = getattr(settings, "CUSTOM_SPECIAL_COVERAGE_PATH", "special_coverage/custom")
        if base_path is None:
            base_path = ""
        return "{0}/{1}_custom.html".format(
            base_path, self.slug.replace("-", "_")
        ).lstrip("/")


def remove_percolator(sender, instance, *args, **kwargs):
    instance._delete_percolator()

pre_delete.connect(remove_percolator, sender=SpecialCoverage)
