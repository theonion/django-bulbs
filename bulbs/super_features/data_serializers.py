from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from bulbs.utils.data_serializers import EntrySerializer


class GuideToChildSerializer(serializers.Serializer):
    entries = EntrySerializer(many=True, required=False, child_label="entry")


class GuideToParentSerializer(serializers.Serializer):
    sponsor_brand_messaging = serializers.CharField(required=False)
    sponsor_product_shot = ImageFieldSerializer(
        required=False,
        label="Sponsor Product Shot (1x1 Image)"
    )
