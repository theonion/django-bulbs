from rest_framework import serializers


class JSONField(serializers.Field):
    """Ensures json dict stays as a dict from db to json and back."""

    def to_representation(self, obj):
        if obj is None:
            return self.default
        return obj

    def to_internal_value(self, data):
        if data is None:
            return self.default
        return data
