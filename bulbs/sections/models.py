from django.db import models
from django.template.defaultfilters import slugify

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content
from djbetty import ImageField
from json_field import JSONField


class Section(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    embed_code = models.TextField(default="", blank=True)
    section_logo = ImageField(null=True, blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    promoted = models.BooleanField(default=False)
    query = JSONField(default={}, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Saving ensures that the slug, if not set, is set to the slugified name."""

        if not self.slug:
            self.slug = slugify(self.name)

        # if self.query and self.query != {}:
        #     self._save_percolator()

        return super(Section, self).save(*args, **kwargs)

    # def _save_percolator(self):
    #     """saves the query field as an elasticsearch percolator
    #     """
    #     index = Content.search_objects.mapping.index
    #     query_filter = self.get_content().to_dict()

    def get_content(self):
        """performs es search and gets content objects
        """
        if "query" in self.query:
            q = self.query["query"]
        else:
            q = self.query
        search = custom_search_model(Content, q, field_map={
            # "feature-type": "feature_type.slug",
            "tag": "tags.slug",
            "content-type": "_type",
            })
        return search