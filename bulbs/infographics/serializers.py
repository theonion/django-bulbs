from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer
from .models import BaseInfographic
from .utils import get_data_serializer


class InfographicDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer = get_data_serializer(int(self.parent.initial_data.get("infographic_type")))
        return serializer().to_internal_value(data)

    def to_representation(self, obj):
        if hasattr(self.parent, 'initial_data'):
            infographic_type = self.parent.initial_data.get('infographic_type', None)
        else:
            infographic_type = getattr(self.parent, 'infographic_type')
        serializer_class = get_data_serializer(int(infographic_type))

        # TODO: figure out a more elegant transition for elasticsearch calls.
        if type(obj).__name__ == 'InnerObjectWrapper':
            obj = obj.__dict__.get('_d_')
        serializer = serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class InfographicSerializer(ContentSerializer):

    data = InfographicDataField(required=False)

    class Meta:
        model = BaseInfographic

    def to_representation(self, obj):
        self.infographic_type = getattr(obj, 'infographic_type')
        return super(InfographicSerializer, self).to_representation(obj)
