from django.db import models
from django.template.defaultfilters import slugify
from json_field import JSONField

from bulbs.campaigns.models import Campaign
from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content


class SpecialCoverage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    query = JSONField(default={}, blank=True)
    videos = JSONField(default=[], blank=True)
    active = models.BooleanField(default=False)
    promoted = models.BooleanField(default=False)
    campaign = models.ForeignKey(Campaign, null=True, default=None, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(SpecialCoverage, self).save(*args, **kwargs)

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
    def contents(self):
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
