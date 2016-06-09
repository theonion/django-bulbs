from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from .serializers import BaseInfographicSerializer, InfographicDataField


def get_and_check_attribute(obj, attr_name):
    attribute = getattr(obj, attr_name)
    if not attribute:
        raise AttributeError("The provided object has no '{}' attribute.".format(attr_name))
    return attribute


class InfographicMetadataMixin(SimpleMetadata):

    def get_custom_metadata(self, serializer, view):
        fields_metadata = dict()

        child = getattr(serializer, "child", None)
        if child:
            return self.get_custom_metadata(child, view)
        else:
            if hasattr(serializer, "__call__"):
                serializer_instance = serializer()
            else:
                serializer_instance = serializer
            for field_name, field in serializer_instance.get_fields().items():
                if isinstance(field, InfographicDataField):
                    serializer = view.get_object().get_data_serializer()
                    fields_metadata[field_name] = self.get_custom_metadata(serializer, view)
                elif isinstance(field, serializers.BaseSerializer):
                    fields_metadata[field_name] = self.get_custom_metadata(field, view)
                else:
                    fields_metadata[field_name] = self.get_field_info(field)
        return {
            "fields": fields_metadata
        }

    def determine_metadata(self, request, view):
        # data = super(InfographicMetadataMixin, self).determine_metadata(request, view)
        serializer_class = view.get_serializer_class()
        if issubclass(serializer_class, BaseInfographicSerializer):
            data = self.get_custom_metadata(serializer_class, view)
            return data
        return {
            "status": "ok"
        }
