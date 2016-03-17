from django.conf import settings
from django.db import models

from elasticsearch import Elasticsearch
from json_field import JSONField

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content


es = Elasticsearch(settings.ES_CONNECTIONS["default"]["hosts"])


class InlineRecircMixin(models.Model):

    query = JSONField(default={}, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super(InlineRecircMixin, self).clean()
        self.clean_query()

    def clean_query(self):
        """
        Removes any `None` value from an elasticsearch query.
        """
        if self.query and self.query != {}:
            for key, value in self.query.items():
                if isinstance(value, list) and None in value:
                    self.query[key] = [v for v in value if v is not None]

    def save(self, *args, **kwargs):
        self.clean()

        super(InlineRecircMixin, self).save(*args, **kwargs)

        if self.query and self.query != {}:
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
        index = Content.seach_objects.mapping.index
        es.delete(
            index=index,
            doc_type=".percolator",
            id=self.es_id,
            refresh=True,
            ignore=404
        )

    def get_content(self, published=True):
        """performs es search and gets content objects
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        search = custom_search_model(Content, q, published=published, field_map={
            "feature_type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        })
        return search

    @property
    def es_id(self):
        return "inlinerecirc.{}".format(self.id)

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
