from rest_framework import serializers

from bulbs.content.models import Content
from bulbs.content.serializers import ContentSerializer, ContentTypeField

from .models import PZone
from .operations import PZoneOperation, InsertOperation, DeleteOperation, ReplaceOperation


class PZoneField(serializers.Field):
    # def field_to_native(self, obj, field_name):
    #     data = []
    #     for content in obj:
    #         data.append(ContentSerializer(instance=content).data)

    #     return data

    def to_representation(self, obj):
        data = []
        bulk_content = Content.objects.in_bulk([content_data["id"] for content_data in obj])
        for content_data in obj:
            content = bulk_content[content_data["id"]]
            data.append(ContentSerializer(instance=content).data)
        return data

    def to_internal_value(self, data):
        return [{"id": content_data["id"]} for content_data in data]


class PZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PZone
        exclude = ("data",)

    content = PZoneField(source="data", required=False)


class _PZoneOperationSerializer(serializers.ModelSerializer):
    """Parent class of pzone operation serializers."""

    type_name = ContentTypeField(source="polymorphic_ctype_id")
    pzone = serializers.PrimaryKeyRelatedField(queryset=PZone.objects.all())
    when = serializers.DateTimeField()
    applied = serializers.BooleanField(default=False)
    content = serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())
    content_title = serializers.SerializerMethodField()

    class Meta:
        model = PZoneOperation

    def get_content_title(self, obj):
        """Get content's title."""
        return Content.objects.get(id=obj.content.id).title


class InsertOperationSerializer(_PZoneOperationSerializer):

    index = serializers.IntegerField(min_value=0)

    class Meta:
        model = InsertOperation


class ReplaceOperationSerializer(_PZoneOperationSerializer):

    index = serializers.IntegerField(min_value=0)

    class Meta:
        model = ReplaceOperation


class DeleteOperationSerializer(_PZoneOperationSerializer):

    class Meta:
        model = DeleteOperation
