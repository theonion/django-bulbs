from rest_framework import serializers


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