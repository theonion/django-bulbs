from djbetty.serializers import ImageFieldSerializer
from rest_framework import serializers

from .models import VideohubVideo


class VideohubVideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    image = ImageFieldSerializer(allow_null=True, default={})
    hub_url = serializers.CharField(source="get_hub_url", read_only=True)
    embed_url = serializers.CharField(source="get_embed_url", read_only=True)
    api_url = serializers.CharField(source="get_api_url", read_only=True)
    channel_id = serializers.IntegerField()

    class Meta:
        model = VideohubVideo

    def save(self, **kwargs):
        """
        Save and return a list of object instances.
        """
        validated_data = [
            dict(list(attrs.items()) + list(kwargs.items()))
            for attrs in self.validated_data
        ]

        if "id" in validated_data:
            ModelClass = self.Meta.model

            try:
                self.instance = ModelClass.objects.get(id=validated_data["id"])
            except ModelClass.DoesNotExist:
                pass

        return super(VideohubVideoSerializer, self).save(**kwargs)

    def to_internal_value(self, data):
        # Channel info passed as nested object, but we just store integer ID
        channel = data.get('channel')
        if channel and 'id' in channel:
            data['channel_id'] = channel['id']
        return super(VideohubVideoSerializer, self).to_internal_value(data)
