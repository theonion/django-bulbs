from django_enumfield import enum
from elasticsearch_dsl import field

from django.db import models

from djes.models import Indexable

from .enum import Status, TemplateType


class Page(Indexable):

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    notes = models.TextField()
    status = enum.EnumField(Status)
    publish_date = models.DateTimeField(blank=True, null=True)
    template_type = enum.EnumField(TemplateType)
    tunic_campaign_id = models.IntegerField(blank=True, null=True, default=None)
