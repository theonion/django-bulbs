from collections import OrderedDict

from django.utils.encoding import force_text

from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import AuthorField
from .data_serializers import CopySerializer, EntrySerializer, XYEntrySerializer
from .fields import ColorField, RichTextField
from .serializers import InfographicSerializer, InfographicDataField


def get_and_check_attribute(obj, attr_name):
    attribute = getattr(obj, attr_name, None)
    if not attribute:
        raise AttributeError("The provided object has no '{}' attribute.".format(attr_name))
    return attribute


class InfographicMetadata(SimpleMetadata):

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
        serializer_class = view.get_serializer_class()
        if issubclass(serializer_class, InfographicSerializer):
            data = self.get_custom_metadata(serializer_class, view)
            return data
        return super(InfographicMetadata, self).determine_metadata(request, view)

    def get_label_lookup(self, field):
        field_type = self.label_lookup[field]
        if field_type == "field" and hasattr(field, "child_relation"):
            return self.get_label_lookup(field.child_relation)
        return field_type

    def get_field_info(self, field):
        """
        This method is basically a mirror from rest_framework==3.3.3

        We are currently pinned to rest_framework==3.1.1. If we upgrade,
        this can be refactored and simplified to rely more heavily on
        rest_framework's built in logic.
        """

        field_info = OrderedDict()
        field_info["type"] = self.get_label_lookup(field)
        field_info["required"] = getattr(field, "required", False)

        attrs = [
            "field_size", "read_only", "label", "help_text", "min_length", "max_length",
            "min_value", "max_value"
        ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != "":
                field_info[attr] = force_text(value, strings_only=True)

        if getattr(field, "child", None):
            field_info["child"] = self.get_field_info(field.child)
        elif getattr(field, "fields", None):
            field_info["children"] = self.get_serializer_info(field)

        if (not isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)) and
                hasattr(field, "choices")):
            field_info["choices"] = [
                {
                    "value": choice_value,
                    "display_name": force_text(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info

    def get_serializer_info(self, serializer):
        serializer_info = super(InfographicMetadata, self).get_serializer_info(serializer)

        if hasattr(serializer, "child"):
            label = self.label_lookup[serializer.child]
        else:
            label = self.label_lookup[serializer]

        # MIKE PARENT PAY ATTENTION: IDK IF THIS IS PRUDENT. LET'S DISCUSS.
        if label != "field":
            return OrderedDict([
                ("type", label),
                ("fields", serializer_info)
            ])
        return serializer_info

    def get_custom_metadata(self, serializer, view):
        fields_metadata = dict()
        if hasattr(serializer, "__call__"):
            serializer_instance = serializer()
        else:
            serializer_instance = serializer
        for field_name, field in serializer_instance.get_fields().items():
            if isinstance(field, InfographicDataField):
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
