from rest_framework import serializers

from bulbs.utils.fields import RichTextField
from bulbs.utils.data_serializers import CopySerializer, EntrySerializer, BaseEntrySerializer


class XYEntrySerializer(BaseEntrySerializer):
    title = RichTextField(field_size="short")
    copy_x = RichTextField(field_size="long")
    copy_y = RichTextField(field_size="long")


class ComparisonKeySerializer(serializers.Serializer):
    title = RichTextField(field_size="short")
    color = serializers.CharField()
    initial = serializers.CharField()


class ComparisonSerializer(serializers.Serializer):
    key_x = ComparisonKeySerializer()
    key_y = ComparisonKeySerializer()
    entries = XYEntrySerializer(many=True, child_label="entry")


class ListInfographicDataSerializer(serializers.Serializer):
    is_numbered = serializers.BooleanField(default=False)
    entries = EntrySerializer(many=True, required=False, child_label="entry")


class ProConSerializer(serializers.Serializer):
    body = RichTextField(required=True, field_size="long")
    pro = CopySerializer(many=True)
    con = CopySerializer(many=True)


class StrongSideWeakSideSerializer(serializers.Serializer):
    body = RichTextField(required=True, field_size="long")
    strong = CopySerializer(many=True)
    weak = CopySerializer(many=True)


class TimelineSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False, child_label="entry")
