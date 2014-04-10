from rest_framework import serializers
from .models import ContentList


class ContentListField(serializers.WritableField):
    def field_to_native(self, obj, field_name):
        data = []
        for content in obj:
            serializer = content.get_serializer_class()
            data.append(serializer(instance=content).data)

        return data

    def from_native(self, data):
        return [{"id": content_data["id"]} for content_data in data]


class ContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentList
        exclude = ("data",)

    content = ContentListField(source="data")
