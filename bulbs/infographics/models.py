from django.db import models

import jsonfield
from django_enumfield import enum
from elasticsearch_dsl import field

from bulbs.content.models import Content
from .enum import InfographicType
from .utils import get_data_serializer


class AbstractInfographic(models.Model):

    infographic_type = enum.EnumField(InfographicType)
    data = jsonfield.JSONField()

    class Meta:
        abstract = True

    def get_infographic_type_name(self):
        return InfographicType.label(self.infographic_type)

    def get_data_serializer(self):
        return get_data_serializer(self.infographic_type)

    def validate_data_field(self):
        Serializer = self.get_data_serializer()  # NOQA
        Serializer(data=self.data).is_valid(raise_exception=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AbstractInfographic, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_data_field()
        return super(AbstractInfographic, self).clean(*args, **kwargs)


class BaseInfographic(Content, AbstractInfographic):

    class Mapping(Content.Mapping):
        data = field.Object()

        class Meta:
            # Necessary to allow for our data field to store appropriately in Elasticsearch.
            # A potential alternative could be storing as a string., we should assess the value.
            dynamic = False

    @classmethod
    def get_serializer_class(cls):
        from .serializers import InfographicSerializer
        return InfographicSerializer
