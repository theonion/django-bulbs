from django.db import models
from django.template.defaultfilters import slugify

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

        return super(Section, self).save(*args, **kwargs)
