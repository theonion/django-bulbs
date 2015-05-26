from rest_framework import serializers
from rest_framework.utils import model_meta

from djbetty.serializers import ImageFieldSerializer

from .models import Campaign, CampaignPixel


class PixelTypeField(serializers.Field):
    """
    Pixel 'type' objects serialized to/from label/identifier
    """
    def to_representation(self, obj):
        return dict(CampaignPixel.PIXEL_TYPES)[obj]

    def to_internal_value(self, data):
        if isinstance(data, int):
            return data
        return dict((label, value)
                for value, label in CampaignPixel.PIXEL_TYPES)[data]


class CampaignPixelField(serializers.ModelSerializer):

    pixel_type = PixelTypeField()

    class Meta:
        model = CampaignPixel
        exclude = ("campaign",)

    def save(self, campaign=None):
        self.instance.campaign = campaign
        return super(CampaignPixelField, self).save()


class CampaignSerializer(serializers.ModelSerializer):

    sponsor_logo = ImageFieldSerializer(required=False)
    pixels = CampaignPixelField(many=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    class Meta:
        model = Campaign

    def create(self, validated_data):
        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        instance = ModelClass.objects.create(**validated_data)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:

            pixel_serializer = CampaignPixelField(data=many_to_many["pixels"], many=True)
            if not pixel_serializer.is_valid():
                raise Exception("Ivalid pixel data")
            pixel_serializer.save(campaign=instance)

        return instance

    def update(self, instance, validated_data):

        pixels_data = validated_data.pop("pixels")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if pixels_data:
            existing_pixel_ids = list(instance.pixels.values_list("id", flat=True))
            for pixel_data in pixels_data:
                if pixel_data.get("id") in existing_pixel_ids:
                    existing_pixel_ids.remove(pixel_data["id"])

            pixel_serializer = CampaignPixelField(data=pixels_data, many=True)
            if not pixel_serializer.is_valid():
                raise Exception("Ivalid pixel data")
            pixel_serializer.save(campaign=instance)

            for pixel_id in existing_pixel_ids:
                print(pixel_id)
                # We need to remove these...
                CampaignPixel.objects.get(id=pixel_id).delete()
        else:
            for pixel in instance.pixels.all():
                pixel.delete()

        return instance
