from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey

import jsonfield
from elasticsearch_dsl import field

from bulbs.content.models import Content
from bulbs.super_features.utils import get_superfeature_choices


GUIDE_TO = 'GUIDE_TO'
BASE_CHOICES = (
    (GUIDE_TO, 'Guide To'),
)

SF_CHOICES = get_superfeature_choices()


class SuperFeatureRelation(models.Model):
    parent = GenericForeignKey('content_type', 'object_id')
    child = GenericForeignKey('content_type', 'object_id')
    ordering = models.IntegerField()


class AbstractSuperFeature(models.Model):
    notes = models.TextField()
    superfeature_type = models.CharField(choices=SF_CHOICES, max_length=255)
    data = jsonfield.JSONField()

    class Meta:
        abstract = True

    @property
    def is_child(self):
        pass

    def get_data_serializer(self):
        from bulbs.super_features.data_serializers import GuideToSerializer

        serializer = {
            "GUIDE_TO": GuideToSerializer
        }.get(self.superfeature_type, None)

        return serializer

    def validate_data_field(self):
        Serializer = self.get_data_serializer()  # NOQA
        Serializer(data=self.data).is_valid(raise_exception=True)

    def save(self, *args, **kwargs):
        self.full_clean()
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

    @classmethod
    def get_serializer_class(cls):
        from bulbs.super_features.serializers import BaseSuperFeatureSerializer
        return BaseSuperFeatureSerializer
