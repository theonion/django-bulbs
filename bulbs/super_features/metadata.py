from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import AuthorField
from bulbs.utils.fields import RichTextField
from bulbs.utils.metadata import BaseSimpleMetadata
from bulbs.utils.data_serializers import CopySerializer, EntrySerializer
from bulbs.super_features.serializers import BaseSuperFeatureDataField
from bulbs.super_features.utils import get_superfeature_serializer

SUPERFEATURE_SERIALIZER = get_superfeature_serializer()


class BaseSuperFeatureMetadata(BaseSimpleMetadata):
    custom_serializer = SUPERFEATURE_SERIALIZER
    custom_data_field = BaseSuperFeatureDataField

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

    def get_custom_field_name(self, view):
        obj = view.get_object()
        serializer = obj.get_data_serializer(obj.superfeature_type)
        return self.get_custom_metadata(serializer, view)
