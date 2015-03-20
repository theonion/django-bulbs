import json

from rest_framework import serializers


class JSONField(serializers.WritableField):
    """Field that is stored in the database as a JSON formatted string, that
    should be retrieved as a dictionary."""

    def to_native(self, obj):
        """When being serialized into JSON, this field should be deserialized first
        so that the parent serializer can reseralize it into an object that is a
        component of the larger JSON string."""

        if not obj:
            # object is nothing, just use the default
            return self.default
        elif isinstance(obj, basestring):
            # object is a string, make sure we deserialize it into an object
            return json.loads(obj)
        else:
            # otherwise it's already an object, just return it
            return obj

    def from_native(self, data):
        """When being dezerialized from JSON, this field should be transformed
        into a string as it would be represented in the database."""

        if not data:
            return json.dumps(self.default)
        return json.dumps(data)
