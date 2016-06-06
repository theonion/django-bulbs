from djbetty.serializers import ImageFieldSerializer
from rest_framework import serializers


class ListInfographicDataSerializer(serializers.Serializer):
    is_numbered = serializers.BooleanField(default=False)
    title = serializers.CharField(required=True, max_length=256)
    copy = serializers.CharField(required=False)
