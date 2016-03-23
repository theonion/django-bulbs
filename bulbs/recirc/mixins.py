from copy import deepcopy

from django.conf import settings
from django.db import models

from elasticsearch import Elasticsearch
from json_field import JSONField

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content


es = Elasticsearch(settings.ES_CONNECTIONS["default"]["hosts"])


class BaseQueryMixin(models.Model):

    query = JSONField(default={}, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super(BaseQueryMixin, self).clean()
        self.clean_query()

    def clean_query(self):
        """
        Removes any `None` value from an elasticsearch query.
        """
        if self.query:
            for key, value in self.query.items():
                if isinstance(value, list) and None in value:
                    self.query[key] = [v for v in value if v is not None]

    def save(self, *args, **kwargs):
        self.clean()
        super(BaseQueryMixin, self).save()

    def get_recirc_content(self, published=True):
        """gets the first 3 content objects in the `included_ids`
        """

        # NOTE: set included_ids to just be the first 3 ids,
        # otherwise search will return last 3 items
        q = self.get_query()
        q['included_ids'] = q['included_ids'][:3]

        search = custom_search_model(Content, q, published=published, field_map={
            "feature_type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        })
        return search

    def get_full_recirc_content(self, published=True):
        """performs es search and gets all content objects
        """
        q = self.get_query()
        search = custom_search_model(Content, q, published=published, field_map={
            "feature_type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type"
        })
        return search

    def get_query(self):
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        return deepcopy(q)

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
        q = self.get_query()
        if "pinned_ids" in q:
            return bool(len(q.get("pinned_ids", [])))
        return False
