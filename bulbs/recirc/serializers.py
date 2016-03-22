from rest_framework import serializers


class RecircContentSerializer(serializers.Serializers):
    image_id = serializers.IntegerField()
    slug = serializers.CharField()
    title = serializers.CharField()
    feature_type = serializers.CharField()
