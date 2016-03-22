from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer


class RecircContentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    thumbnail = ImageFieldSerializer(allow_null=True, read_only=True)
    slug = serializers.CharField()
    title = serializers.CharField()
    feature_type = serializers.CharField()
