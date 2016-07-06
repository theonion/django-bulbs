from rest_framework import serializers

# TODO: Use common EntrySerializer
from bulbs.infographics.data_serializers import EntrySerializer


class GuideToSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)
