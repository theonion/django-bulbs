from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from bulbs.utils.data_serializers import EntrySerializer


class GuideToChildSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)


class GuideToParentSerializer(serializers.Serializer):
    sponsor_text = serializers.CharField(required=False)
    sponsor_image = ImageFieldSerializer(required=False)
