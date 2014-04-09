from rest_framework import serializers
from .models import ContentList


class ContentListField(serializers.WritableField):
    def to_native(self, obj):
        content = []
        for c in obj:
            serializer = c.get_serializer_class()
            content.append(serializer(instance=c).data)
        return content

    def from_native(self, data):
        return [content_data["id"] for content_data in data]


class ContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentList
        exclude = ("data",)

    content = ContentListField(source="content")
