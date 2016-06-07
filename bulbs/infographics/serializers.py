from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer
from .models import BaseInfographic
from .utils import get_data_serializer


class InfographicDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer = get_data_serializer(int(self.parent.initial_data.get("infographic_type")))
        return serializer().to_internal_value(data)

    def to_representation(self, obj):
        serializer = get_data_serializer(int(self.parent.initial_data.get("infographic_type")))
        return serializer().to_representation(obj)


class BaseInfographicSerializer(ContentSerializer):

    data = InfographicDataField()

    class Meta:
        model = BaseInfographic
