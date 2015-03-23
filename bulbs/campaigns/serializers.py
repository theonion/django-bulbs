from rest_framework import serializers

from rest_framework import relations

from bulbs.content.serializers import ImageFieldSerializer

from .models import Campaign, CampaignPixel


def pixel_type_string_to_value(data):
    return dict((label, value)
                for value, label in CampaignPixel.PIXEL_TYPES)[data]


class PixelTypeField(serializers.WritableField):
    """
    Pixel 'type' objects serialized to/from label/identifier
    """
    def to_native(self, obj):
        return dict(CampaignPixel.PIXEL_TYPES)[obj]

    def from_native(self, data):
        return pixel_type_string_to_value(data)


# class CampaignPixelSerializer(serializers.ModelSerializer):
class CampaignPixelField(relations.RelatedField):

    # pixel_type = PixelTypeField()

    # class Meta:
    #     model = CampaignPixel
    #     exclude = ('campaign',)

    read_only = False

    def from_native(self, data):
        print(self.parent.object)
        # raise Exception()
        #import pytest; pytest.set_trace()
        if "id" in data:
            pixel = CampaignPixel.objects.get(id=data["id"])
        else:
            #import pytest; pytest.set_trace()
            url = data["url"]
            pixel_type = pixel_type_string_to_value(data["pixel_type"])
            pixel = CampaignPixel.objects.create(url=url,
                                                 pixel_type=pixel_type,
                                                 campaign=self.parent.object)
        return pixel


class CampaignSerializer(serializers.ModelSerializer):

    sponsor_logo = ImageFieldSerializer(required=False)
    pixels = CampaignPixelField(many=True)

    class Meta:
        model = Campaign
