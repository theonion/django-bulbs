from djbetty.serializers import ImageFieldSerializer
from rest_framework import serializers

from .fields import RichTextField


class CopySerializer(serializers.Serializer):
    copy = RichTextField(required=True, field_size="long")


class ItemSerializer(CopySerializer):
    title = RichTextField(field_size="short")
    image = ImageFieldSerializer(required=False)


class XYItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    copy_x = serializers.CharField()
    copy_y = serializers.CharField()


class ComparisonKeySerializer(serializers.Serializer):
    title = serializers.CharField()
    color = serializers.CharField()
    initial = serializers.CharField()


class ComparisonSerializer(serializers.Serializer):
    key = ComparisonKeySerializer()
    items = XYItemSerializer(many=True)


class ListInfographicDataSerializer(serializers.Serializer):
    is_numbered = serializers.BooleanField(default=False)
    items = ItemSerializer(many=True, required=False)


class ProConSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    pro = CopySerializer(many=True)
    con = CopySerializer(many=True)


class StrongSideWeakSideSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    strong = CopySerializer(many=True)
    weak = CopySerializer(many=True)


class TimelineSerializer(serializers.Serializer):
    items = ItemSerializer(many=True, required=False)
