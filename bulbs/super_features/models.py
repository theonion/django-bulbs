import jsonfield
from django_enumfield import enum

from django.db import models
from django.template.defaultfilters import slugify

from bulbs.content.models import Content
from bulbs.super_features.enum import Status, SuperFeatureTemplate


class SuperFeature(Content):

    notes = models.TextField()
    status = enum.EnumField(Status)
    template = enum.EnumField(SuperFeatureTemplate)
    data = jsonfield.JSONField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50]
        return super(SuperFeature, self).save(*args, **kwargs)
