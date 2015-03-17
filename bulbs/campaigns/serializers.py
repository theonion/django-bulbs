from rest_framework import serializers

from bulbs.content.serializers import ImageFieldSerializer

from .models import Campaign, CampaignPixel


class CampaignTypeField(serializers.WritableField):
    """
    Campaign 'type' objects serialized to/from label/identifier
    """
    def to_native(self, obj):
        return dict(CampaignPixel.CHOICES)[obj]

    def from_native(self, data):
        return dict((label, value)
                    for value, label in CampaignPixel.CHOICES)[data]


class CampaignPixelSerializer(serializers.ModelSerializer):

    campaign_type = CampaignTypeField()

    class Meta:
        model = CampaignPixel
        exclude = ('campaign',)


class CampaignSerializer(serializers.ModelSerializer):

    sponsor_logo = ImageFieldSerializer(required=False)
    pixels = CampaignPixelSerializer(many=True)

    class Meta:
        model = Campaign
