from rest_framework import serializers

from bulbs.content.models import Content
from bulbs.content.serializers import ContentSerializer
from bulbs.super_features.models import BaseSuperFeature, ContentRelation
from bulbs.super_features.utils import get_data_serializer


class ContentRelationSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent', queryset=Content.objects.all()
    )
    child_id = serializers.PrimaryKeyRelatedField(
        source='child', queryset=Content.objects.all()
    )

    class Meta:
        model = ContentRelation
        fields = ('id', 'parent_id', 'child_id', 'ordering')


class BaseSuperFeatureDataField(serializers.Field):

    def to_internal_value(self, data):
        serializer = get_data_serializer(
            self.parent.initial_data.get("superfeature_type")
        )
        return serializer().to_internal_value(data)

    def to_representation(self, obj):
        serializer_class = get_data_serializer(
            self.parent.initial_data.get("superfeature_type")
        )
        serializer = serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        return serializer.data


class BaseSuperFeatureSerializer(ContentSerializer):
    data = BaseSuperFeatureDataField(required=False)

    class Meta:
        model = BaseSuperFeature


class BaseSuperFeaturePartialSerializer(ContentSerializer):

    class Meta:
        model = BaseSuperFeature
        fields = ('id', 'internal_name', 'title')
