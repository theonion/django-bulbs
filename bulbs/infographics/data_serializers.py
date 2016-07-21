from rest_framework import serializers

from bulbs.utils.fields import RichTextField
from bulbs.utils.data_serializers import CopySerializer, EntrySerializer, BaseEntrySerializer
from .fields import ColorField


class XYEntrySerializer(BaseEntrySerializer):
    title = RichTextField(required=False, field_size="short")
    copy_x = RichTextField(field_size="long")
    copy_y = RichTextField(field_size="long")


class ComparisonKeySerializer(serializers.Serializer):
    title = RichTextField(required=False, field_size="short")
    color = ColorField(required=False)
    initial = serializers.CharField()


class ComparisonSerializer(serializers.Serializer):
    key_x = ComparisonKeySerializer(required=False)
    key_y = ComparisonKeySerializer(required=False)
    entries = XYEntrySerializer(required=False, many=True, child_label="entry")


class ListInfographicDataSerializer(serializers.Serializer):
    is_numbered = serializers.BooleanField(default=False)
    entries = EntrySerializer(many=True, required=False, child_label="entry")


class ProConSerializer(serializers.Serializer):
    body = RichTextField(required=False, field_size="long")
    pro = CopySerializer(required=False, many=True)
    con = CopySerializer(required=False, many=True)


class StrongSideWeakSideSerializer(serializers.Serializer):
    body = RichTextField(required=False, field_size="long")
    strong = CopySerializer(required=False, many=True)
    weak = CopySerializer(required=False, many=True)


class TimelineSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False, child_label="entry")
