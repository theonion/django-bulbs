from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

# TODO: Use common EntrySerializer
from bulbs.infographics.data_serializers import EntrySerializer


class GuideToChildSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)


class GuideToParentSerializer(serializers.Serializer):
    sponsor_text = serializers.CharField()
    sponsor_image = ImageFieldSerializer(required=False)
