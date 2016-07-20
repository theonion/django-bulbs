from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Basic model serializer for notifications.Notification."""
    class Meta:
        model = Notification
