from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class ContentTypeField(serializers.WritableField):
    """Converts between natural key for native use and integer for non-native."""
    def to_native(self, value):
        """Convert to natural key."""
        content_type = ContentType.objects.get_for_id(value)
        return "_".join(content_type.natural_key())

    def from_native(self, value):
        """Convert to integer id."""
        natural_key = value.split("_")
        content_type = ContentType.objects.get_by_natural_key(*natural_key)
        return content_type.id


class PolymorphicSerializerMixin(object):
    """Serialize a mix of polymorphic models with their own serializer classes."""
    def to_native(self, value):
        if value:
            if hasattr(value, "get_serializer_class"):
                ThisSerializer = value.get_serializer_class()
            else:
                class ThisSerializer(serializers.ModelSerializer):
                    class Meta:
                        model = value.__class__

            serializer = ThisSerializer(context=self.context)
            return serializer.to_native(value)
        else:
            return super(PolymorphicSerializerMixin, self).to_native(value)