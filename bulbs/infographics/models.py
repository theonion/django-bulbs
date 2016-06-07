import jsonfield
from django_enumfield import enum
from elasticsearch_dsl import field

from bulbs.content.models import Content
from .data_serializers import (
    ComparisonSerializer, ListInfographicDataSerializer, ProConSerializer,
    StrongSideWeakSideSerializer, TimelineSerializer
)


class InfographicType(enum.Enum):
    LIST = 0
    TIMELINE = 1
    STRONGSIDE_WEAKSIDE = 2
    PRO_CON = 3
    COMPARISON = 4


class BaseInfographic(Content):

    infographic_type = enum.EnumField(InfographicType)
    data = jsonfield.JSONField()

    class Mapping(Content.Mapping):
        data = field.Object()

        class Meta:
            # Necessary to allow for our data field to store appropriately in Elasticsearch.
            # A potential alternative could be storing as a string., we should assess the value.
            dynamic = False

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(BaseInfographic, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_data_field()
        return super(BaseInfographic, self).clean(*args, **kwargs)

    def validate_data_field(self):
        Serializer = self.get_data_serializer()  # NOQA
        Serializer(data=self.data).is_valid(raise_exception=True)

    def get_data_serializer(self):
        serializer = {
            InfographicType.LIST: ListInfographicDataSerializer,
            InfographicType.TIMELINE: TimelineSerializer,
            InfographicType.STRONGSIDE_WEAKSIDE: StrongSideWeakSideSerializer,
            InfographicType.PRO_CON: ProConSerializer,
            InfographicType.COMPARISON: ComparisonSerializer
        }.get(self.infographic_type, None)
        if serializer is None:
            raise KeyError(
                """The requested Infographic does not have a configured serializer."""
            )
        return serializer
