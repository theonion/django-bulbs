from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import AuthorField

from bulbs.utils.fields import RichTextField
from bulbs.utils.metadata import BaseSimpleMetadata
from bulbs.utils.data_serializers import CopySerializer, EntrySerializer
from .data_serializers import (
    ComparisonKeySerializer, XYEntrySerializer
)
from .fields import ColorField
from .serializers import InfographicSerializer, InfographicDataField


class InfographicMetadata(BaseSimpleMetadata):
    custom_serializer = InfographicSerializer
    custom_data_field = InfographicDataField

    @property
    def label_lookup(self):
        mapping = SimpleMetadata.label_lookup.mapping
        mapping.update({
            AuthorField: "string",
            ColorField: "color",
            ComparisonKeySerializer: "object",
            CopySerializer: "array",
            EntrySerializer: "array",
            XYEntrySerializer: "array",
            ImageFieldSerializer: "image",
            RichTextField: "richtext"
        })
        return ClassLookupDict(mapping)

    def get_custom_field_name(self, view):
        serializer = view.get_object().get_data_serializer()
        return self.get_custom_metadata(serializer, view)
