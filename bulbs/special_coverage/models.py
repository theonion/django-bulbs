from django.conf import settings
from django.db.models.signals import pre_delete
from django.db import models
from django.template.defaultfilters import slugify
from elasticsearch import Elasticsearch
from json_field import JSONField

from bulbs.campaigns.models import Campaign
from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content


es = Elasticsearch(settings.ES_URLS)


class SpecialCoverage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    query = JSONField(default={}, blank=True)
    videos = JSONField(default=[], blank=True)
    active = models.BooleanField(default=False)
    promoted = models.BooleanField(default=False)
    campaign = models.ForeignKey(
        Campaign, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    # Property-specific custom configuration
    config = JSONField(default={}, blank=True)

    def __unicode__(self):
        return self.name

    def clean(self):
        super(SpecialCoverage, self).clean()
        if self.query and self.query != {}:
            for key, value in self.query.items():
                if isinstance(value, list) and None in value:
                    self.query[key] = [v for v in value if v is not None]

    def save(self, *args, **kwargs):
        """Saving ensures that the slug, if not set, is set to the slugified name."""
        self.clean()
        if not self.slug:
            self.slug = slugify(self.name)

        super(SpecialCoverage, self).save(*args, **kwargs)

        if self.query and self.query != {}:
            if self.active:
                self._save_percolator()
            else:
                self._delete_percolator()

    def _save_percolator(self):
        """saves the query field as an elasticsearch percolator
        """
        index = Content.search_objects.mapping.index
        query_filter = self.get_content().to_dict()

        q = {}

        if "query" in query_filter:
            q = {"query": query_filter.get("query", {})}
        else:
            # We don't know how to save this
            return

        # We'll need this data, to decide which special coverage section to use
        if self.campaign:
            q["sponsored"] = True
            q["start_date"] = self.campaign.start_date
            q["end_date"] = self.campaign.end_date

        es.index(
            index=index,
            doc_type=".percolator",
            body=q,
            id=self.es_id
        )

    def _delete_percolator(self):
        index = Content.search_objects.mapping.index
        es.delete(index=index, doc_type=".percolator", id=self.es_id, refresh=True, ignore=404)

    def get_content(self):
        """performs es search and gets content objects
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        search = custom_search_model(Content, q, field_map={
            "feature-type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        })
        return search

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


def remove_percolator(sender, instance, *args, **kwargs):
    instance._delete_percolator()

pre_delete.connect(remove_percolator, sender=SpecialCoverage)
