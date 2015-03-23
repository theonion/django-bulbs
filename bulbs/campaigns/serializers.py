from django.core.exceptions import ValidationError
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


class CampaignPixelField(relations.RelatedField):

    read_only = False

    def to_native(self, obj):
        return {'id': obj.id,
                'pixel_type': dict(CampaignPixel.PIXEL_TYPES)[obj.pixel_type],
                'url': obj.url}

    def from_native(self, data):
        if "id" in data:
            pixel = CampaignPixel.objects.get(id=data["id"])
        else:
            # Django REST Framework has poor support for nested relations (for new parent objects,
            # this from_native() method would be called before parent object is saved/available).
            if self.parent.object is None:
                raise ValidationError("New campaigns must be saved once before adding pixels.")

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
