from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer
from bulbs.super_features.models import BaseSuperFeature
from bulbs.super_features.utils import get_data_serializer


class BaseSuperFeatureDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer_class = get_data_serializer(
            self.parent.initial_data.get("superfeature_type")
        )
        return serializer_class().to_internal_value(data)

    def to_representation(self, obj):
        serializer_class = get_data_serializer(
            self.parent.initial_data.get("superfeature_type")
        )
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
