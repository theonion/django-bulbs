from django.db import models

import jsonfield
from elasticsearch_dsl import field

from bulbs.content.models import Content
from bulbs.super_features.utils import get_superfeature_choices, get_data_serializer


GUIDE_TO_HOMEPAGE = 'GUIDE_TO_HOMEPAGE'
GUIDE_TO_ENTRY = 'GUIDE_TO_ENTRY'
BASE_CHOICES = (
    (GUIDE_TO_HOMEPAGE, 'Guide To Homepage'),
    (GUIDE_TO_ENTRY, 'Guide To Entry'),
)

SF_CHOICES = get_superfeature_choices()


class ContentRelation(models.Model):
    parent = models.ForeignKey(Content, related_name="parent")
    child = models.ForeignKey(Content, related_name="child")
    ordering = models.IntegerField()

    class Meta:
        unique_together = ('parent', 'ordering')


class AbstractSuperFeature(models.Model):
    notes = models.TextField(null=True, blank=True, default='')
    internal_name = models.CharField(null=True, blank=True, max_length=255)
    superfeature_type = models.CharField(choices=SF_CHOICES, max_length=255)
    default_child_type = models.CharField(choices=SF_CHOICES, max_length=255, null=True, blank=True)
    data = jsonfield.JSONField()

    class Meta:
        abstract = True

    @classmethod
    def get_data_serializer(cls, name):
        return get_data_serializer(name)

    def validate_data_field(self):
        Serializer = self.get_data_serializer(self.superfeature_type)  # NOQA
        Serializer(data=self.data).is_valid(raise_exception=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_child:
            self.index(save=False)

        return super(AbstractSuperFeature, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_data_field()
        return super(AbstractSuperFeature, self).clean(*args, **kwargs)


class BaseSuperFeature(Content, AbstractSuperFeature):

    class Mapping(Content.Mapping):
        data = field.Object()

        class Meta:
            # Necessary to allow for our data field to store appropriately in Elasticsearch.
            # A potential alternative could be storing as a string., we should assess the value.
            dynamic = False

    @property
    def is_parent(self):
        return ContentRelation.objects.filter(parent=self).exists()

    @property
    def is_child(self):
        return ContentRelation.objects.filter(child=self).exists()

    @classmethod
    def get_serializer_class(cls):
        from bulbs.super_features.serializers import BaseSuperFeatureSerializer
        return BaseSuperFeatureSerializer
