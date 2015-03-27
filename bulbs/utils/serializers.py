import json

from rest_framework import serializers


class JSONField(serializers.WritableField):
    """Ensures json dict stays as a dict from db to json and back."""

    def to_native(self, obj):
        if obj is None:
            return self.default
        return obj

    def from_native(self, data):
        if data is None:
            return self.default
        return data

