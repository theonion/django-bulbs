from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import AuthorField
from bulbs.utils.fields import RichTextField
from bulbs.utils.metadata import BaseSimpleMetadata
from bulbs.infographics.data_serializers import CopySerializer, EntrySerializer
from bulbs.super_features.serializers import BaseSuperFeatureSerializer, BaseSuperFeatureDataField


class BaseSuperFeatureMetadata(BaseSimpleMetadata):

    @property
    def label_lookup(self):
        mapping = SimpleMetadata.label_lookup.mapping
        mapping.update({
            AuthorField: "string",
            CopySerializer: "array",
            EntrySerializer: "array",
            ImageFieldSerializer: "image",
            RichTextField: "richtext"
        })
        return ClassLookupDict(mapping)

    def determine_metadata(self, request, view):
        serializer_class = view.get_serializer_class()
        if issubclass(serializer_class, BaseSuperFeatureSerializer):
            data = self.get_custom_metadata(serializer_class, view)
            return data
        return super(BaseSuperFeatureMetadata, self).determine_metadata(request, view)

    def get_custom_metadata(self, serializer, view):
        fields_metadata = dict()
        if hasattr(serializer, "__call__"):
            serializer_instance = serializer()
        else:
            serializer_instance = serializer
        for field_name, field in serializer_instance.get_fields().items():
            if isinstance(field, BaseSuperFeatureDataField):
                if view.suffix != "List":
                    serializer = view.get_object().get_data_serializer()
                    fields_metadata[field_name] = self.get_custom_metadata(serializer, view)
            elif isinstance(field, serializers.BaseSerializer):
                fields_metadata[field_name] = self.get_serializer_info(field)
            else:
                fields_metadata[field_name] = self.get_field_info(field)
        return {
            "fields": fields_metadata
        }
