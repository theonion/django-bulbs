from bulbs.content.serializers import ImageFieldSerializer
from rest_framework import serializers

from .models import VideoHubVideo


class VideoHubVideoSerializer(serializers.ModelSerializer):
    poster = ImageFieldSerializer(caption_field="poster_caption", alt_field="poster_alt", required=False)
    hub_url = serializers.CharField(source="get_hub_url", read_only=True)
    embed_url = serializers.CharField(source="get_embed_url", read_only=True)
    api_url = serializers.CharField(source="get_api_url", read_only=True)

    class Meta:
        model = VideoHubVideo

    def from_native(self, data, *args, **kwargs):
        """prevents DRF from creating a new row
        """
        identity = self.get_identity(data)
        obj = None
        if identity:
            try:
                obj = self.opts.model.objects.get(id=identity)
            except self.opts.model.DoesNotExist:
                pass
            else:
                dirty = False
                for field_name, field_serializer in self.fields.items():
                    val = field_serializer.from_native(data.get(field_name))
                    if hasattr(obj, field_name):
                        if getattr(obj, field_name) != val:
                            setattr(obj, field_name, val)
                            dirty = True
                if dirty:
                    obj.save()
        if obj is None:
            obj = super(VideoHubVideoSerializer, self).from_native(data, *args, **kwargs)
        return obj
