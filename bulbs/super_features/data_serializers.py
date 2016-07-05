from rest_framework import serializers


class EntrySerializer(serializers.Serializer):
    pass


class GuideToSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False)
