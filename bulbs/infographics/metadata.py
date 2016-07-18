from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import AuthorField
from bulbs.utils.fields import ColorField, RichTextField
from bulbs.utils.metadata import BaseSimpleMetadata
from .data_serializers import CopySerializer, EntrySerializer, XYEntrySerializer
from .serializers import InfographicSerializer, InfographicDataField


class InfographicMetadata(BaseSimpleMetadata):

    @property
    def label_lookup(self):
        mapping = SimpleMetadata.label_lookup.mapping
        mapping.update({
            AuthorField: "string",
            ColorField: "color",
            CopySerializer: "array",
            EntrySerializer: "array",
            XYEntrySerializer: "array",
            ImageFieldSerializer: "image",
            RichTextField: "richtext"
        })
        return ClassLookupDict(mapping)

    def determine_metadata(self, request, view):
        return super(InfographicMetadata, self).determine_metadata(
            request, view, InfographicSerializer
        )

    def get_custom_field_name(self, view):
        serializer = view.get_object().get_data_serializer()
        return self.get_custom_metadata(serializer, view)

    def get_custom_metadata(self, serializer, view):
        return super(InfographicMetadata, self).get_custom_metadata(
            serializer, view, InfographicDataField
        )
