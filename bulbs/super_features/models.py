from django.db import models

import jsonfield
from django_enumfield import enum
from elasticsearch_dsl import field

from bulbs.content.models import Content
from bulbs.super_features.enum import SuperFeatureType
from bulbs.super_features.utils import get_superfeature_choices


SF_CHOICES = get_superfeature_choices()


class AbstractSuperFeature(models.Model):
    notes = models.TextField()
    superfeature_type = models.CharField(choices=SF_CHOICES)
    data = jsonfield.JSONField()

    class Meta:
        abstract = True

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
