from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer
from .models import BaseInfographic
from .utils import get_data_serializer


class InfographicDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer = get_data_serializer(int(self.parent.initial_data.get("infographic_type")))
        return serializer().to_internal_value(data)

    def to_representation(self, obj):
        serializer_class = get_data_serializer(
            int(self.parent.initial_data.get("infographic_type"))
        )
        serializer = serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class InfographicSerializer(ContentSerializer):

    data = InfographicDataField(required=False)

    class Meta:
        model = BaseInfographic
