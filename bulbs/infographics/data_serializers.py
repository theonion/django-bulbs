from djbetty.serializers import ImageFieldSerializer
from rest_framework import serializers

from .fields import RichTextField


class BaseEntrySerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.child_label = kwargs.pop("child_label", None)
        super(BaseEntrySerializer, self).__init__(*args, **kwargs)


class CopySerializer(serializers.Serializer):
    copy = RichTextField(required=True, field_size="long")


class EntrySerializer(BaseEntrySerializer, CopySerializer):
    title = RichTextField(field_size="short")
    image = ImageFieldSerializer(required=False)


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
