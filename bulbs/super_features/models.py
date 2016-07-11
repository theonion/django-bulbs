from django.db import models

import jsonfield
from elasticsearch_dsl import field

from bulbs.content.models import Content
from bulbs.super_features.utils import get_superfeature_choices


GUIDE_TO_HOME = 'GUIDE_TO_HOME'
GUIDE_TO_PAGE = 'GUIDE_TO_PAGE'
BASE_CHOICES = (
    (GUIDE_TO_HOME, 'Guide To Home'),
    (GUIDE_TO_PAGE, 'Guide To Page'),
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
    superfeature_type = models.CharField(choices=SF_CHOICES, max_length=255)
    data = jsonfield.JSONField()

    class Meta:
        abstract = True

    def get_data_serializer(self):
        from bulbs.super_features.data_serializers import (GuideToChildSerializer,
                                                           GuideToParentSerializer)

        sf_type = getattr(self, 'superfeature_type', self)
        serializer = {
            GUIDE_TO_HOME: GuideToParentSerializer,
            GUIDE_TO_PAGE: GuideToChildSerializer
        }.get(sf_type, None)

        if serializer is None:
            raise KeyError('The requested SuperFeature does not have a registered serializer')

        return serializer

    def validate_data_field(self):
        Serializer = self.get_data_serializer()  # NOQA
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
