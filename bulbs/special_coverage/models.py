from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from elasticsearch import Elasticsearch
from json_field import JSONField

from bulbs.campaigns.models import Campaign
from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content


es = Elasticsearch(settings.ES_URLS)
index = Content.get_index_name()


class SpecialCoverage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    query = JSONField(default={}, blank=True)
    videos = JSONField(default=[], blank=True)
    active = models.BooleanField(default=False)
    promoted = models.BooleanField(default=False)
    campaign = models.ForeignKey(Campaign, null=True, default=None, blank=True)

    @classmethod
    def get_doc_type(cls):
        return ".percolator"

    def save(self, *args, **kwargs):
        """Saving ensures that the slug, if not set, is set to the slugified name."""

        if not self.slug:
            self.slug = slugify(self.name)

        if self.query and self.query != {}:
            if self.active:
                self._save_percolator()
            else:
                self._delete_percolator()
        return super(SpecialCoverage, self).save(*args, **kwargs)

    def _save_percolator(self):
        """saves the query field as an elasticsearch percolator
        """
        query_filter = self.get_content().build_search()
        if query_filter.get("filter"):
            q = {
                "query": {
                    "filtered": {
                        "filter": query_filter.get("filter", {})
                    }
                }
            }
            try:
                res = es.create(index=index, doc_type=self.get_doc_type(), body=q, id=self.es_id, refresh=True)
            except Exception, e:
                res = e
        else:
            res = None
        return res

    def _delete_percolator(self):
        try:
            res = es.delete(index=index, doc_type=self.get_doc_type(), id=self.es_id, refresh=True)
        except Exception, e:
            res = e
        return res

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
        return search.full()

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
