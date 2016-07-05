from rest_framework import serializers

from bulbs.super_features.fields import RichTextField


class EntrySerializer(serializers.Serializer):
    copy = RichTextField(required=True, field_size="long")


class GuideToSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)
