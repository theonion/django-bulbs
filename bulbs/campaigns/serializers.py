from rest_framework import serializers

from bulbs.content.serializers import ImageFieldSerializer

from .models import Campaign, CampaignPixel


class PixelTypeField(serializers.WritableField):
    """
    Pixel 'type' objects serialized to/from label/identifier
    """
    def to_native(self, obj):
        return dict(CampaignPixel.PIXEL_TYPES)[obj]

    def from_native(self, data):
        return dict((label, value)
                    for value, label in CampaignPixel.PIXEL_TYPES)[data]


class CampaignPixelField(serializers.ModelSerializer):

    pixel_type = PixelTypeField()

    class Meta:
        model = CampaignPixel
        exclude = ("campaign",)


class CampaignSerializer(serializers.ModelSerializer):

    sponsor_logo = ImageFieldSerializer(required=False)
    pixels = CampaignPixelField(many=True, allow_add_remove=True)

    class Meta:
        model = Campaign
