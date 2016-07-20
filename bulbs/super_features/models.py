from django.db import models

import jsonfield
from elasticsearch_dsl import field

from bulbs.content.models import Content
from bulbs.recirc.mixins import BaseQueryMixin
from bulbs.super_features.utils import get_superfeature_choices
from bulbs.super_features.mixins import SuperFeatureMixin


GUIDE_TO_HOMEPAGE = 'GUIDE_TO_HOMEPAGE'
GUIDE_TO_ENTRY = 'GUIDE_TO_ENTRY'
BASE_CHOICES = (
    (GUIDE_TO_HOMEPAGE, 'Guide To Homepage'),
    (GUIDE_TO_ENTRY, 'Guide To Entry'),
)

SF_CHOICES = get_superfeature_choices()


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
        from bulbs.super_features.data_serializers import (GuideToChildSerializer,
                                                           GuideToParentSerializer)

        serializer = {
            GUIDE_TO_HOMEPAGE: GuideToParentSerializer,
            GUIDE_TO_ENTRY: GuideToChildSerializer
        }.get(name, None)
        if serializer is None:
            raise KeyError('The requested SuperFeature does not have a registered serializer')

        return serializer

    def validate_data_field(self):
        Serializer = self.get_data_serializer(self.superfeature_type)  # NOQA
        Serializer(data=self.data).is_valid(raise_exception=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AbstractSuperFeature, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_data_field()
        return super(AbstractSuperFeature, self).clean(*args, **kwargs)


class BaseSuperFeature(SuperFeatureMixin, Content, AbstractSuperFeature, BaseQueryMixin):
    parent = models.ForeignKey('self', blank=True, null=True)
    ordering = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ('parent', 'ordering')

    class Mapping(Content.Mapping):
        # NOTE: parent is set to integer so DJES doesn't recurse
        parent = field.Integer()
        data = field.Object()

        class Meta:
            # Necessary to allow for our data field to store appropriately in Elasticsearch.
            # A potential alternative could be storing as a string., we should assess the value.
            dynamic = False

    @classmethod
    def get_serializer_class(cls):
        from bulbs.super_features.serializers import BaseSuperFeatureSerializer
        return BaseSuperFeatureSerializer
