from rest_framework import serializers

from bulbs.super_features.fields import RichTextField


# TODO: Move to common file
class CopySerializer(serializers.Serializer):
    copy = RichTextField(required=True, field_size="long")


# TODO: Move to common file
class EntrySerializer(CopySerializer, serializers.Serializer):
    title = RichTextField(field_size="short")


class GuideToSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)
