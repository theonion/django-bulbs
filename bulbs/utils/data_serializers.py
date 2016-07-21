from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from bulbs.utils.fields import RichTextField


class BaseEntrySerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.child_label = kwargs.pop("child_label", None)
        super(BaseEntrySerializer, self).__init__(*args, **kwargs)


class CopySerializer(serializers.Serializer):
    copy = RichTextField(required=True, field_size="long")


class EntrySerializer(BaseEntrySerializer, CopySerializer):
    title = RichTextField(required=False, field_size="short")
    image = ImageFieldSerializer(required=False, default=None, allow_null=True)
