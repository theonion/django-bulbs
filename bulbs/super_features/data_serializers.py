from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from bulbs.utils.fields import RichTextField
from bulbs.utils.data_serializers import BaseEntrySerializer, CopySerializer


class GuideToEntrySerializer(BaseEntrySerializer, CopySerializer):
    image = ImageFieldSerializer(required=False, default=None, allow_null=True)


class GuideToChildSerializer(serializers.Serializer):
    entries = GuideToEntrySerializer(many=True, required=False, child_label="entry")


class GuideToParentSerializer(serializers.Serializer):
    copy = RichTextField(required=False, field_size="long")
    sponsor_brand_messaging = serializers.CharField(required=False)
    sponsor_product_shot = ImageFieldSerializer(
        required=False,
        label="Sponsor Product Shot (1x1 Image)"
    )
