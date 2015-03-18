from django.db import models
from django.template.defaultfilters import slugify
from json_field import JSONField


class SpecialCoverage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, editable=True, unique=True)
    description = models.TextField(default="", blank=True)
    query = JSONField(default={}, blank=True)
    videos = JSONField(default=[], blank=True)
    active = models.BooleanField(default=False)
    promoted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(SpecialCoverage, self).save(*args, **kwargs)
