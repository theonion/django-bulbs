from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer
from bulbs.super_features.models import BaseSuperFeature
from bulbs.super_features.utils import get_superfeature_model


SUPERFEATURE_MODEL = get_superfeature_model()


class BaseSuperFeatureDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer_class = SUPERFEATURE_MODEL.get_data_serializer(
            self.parent.initial_data.get("superfeature_type")
        )
        return serializer_class().to_internal_value(data)

    def to_representation(self, obj):
        if hasattr(self.parent, 'initial_data'):
            sf_type = self.parent.initial_data.get('superfeature_type', None)
        else:
            sf_type = getattr(self.parent, 'superfeature_type')
        serializer_class = SUPERFEATURE_MODEL.get_data_serializer(sf_type)

        # TODO: figure out a more elegant transition for elasticsearch calls.
        if type(obj).__name__ == 'InnerObjectWrapper':
            obj = obj.__dict__.get('_d_')
        serializer = serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class BaseSuperFeatureSerializer(ContentSerializer):
    data = BaseSuperFeatureDataField(required=False)
    ordering = serializers.IntegerField(required=False, allow_null=True, default=None)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=BaseSuperFeature.objects.all(), required=False, allow_null=True, default=None
    )

    class Meta:
        model = BaseSuperFeature


class BaseSuperFeaturePartialSerializer(ContentSerializer):

    class Meta:
        model = BaseSuperFeature
        fields = ('id', 'internal_name', 'title')
