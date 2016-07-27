from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Basic model serializer for notifications.Notification."""

    image = ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        model = Notification
