from djbetty.serializers import ImageFieldSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError


def has_two(value):
    if len(value) != 2:
        raise ValidationError("""key field requires at least 2 entries.""")


class CopySerializer(serializers.Serializer):
    copy = serializers.CharField(required=True)


class ItemSerializer(CopySerializer):
    title = serializers.CharField()
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
    key = ComparisonKeySerializer(many=True, validators=[has_two])
    items = XYItemSerializer(many=True)


class ListInfographicDataSerializer(serializers.Serializer):
    is_numbered = serializers.BooleanField(default=False)
    items = ItemSerializer(many=True)


class ProConSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    pro = CopySerializer(many=True)
    con = CopySerializer(many=True)


class StrongSideWeakSideSerializer(serializers.Serializer):
    body = serializers.CharField(required=True)
    strong = CopySerializer(many=True)
    weak = CopySerializer(many=True)


class TimelineSerializer(serializers.Serializer):
    items = ItemSerializer(many=True)
