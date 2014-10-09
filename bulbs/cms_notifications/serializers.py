from bulbs.cms_notifications.models import CmsNotification
from rest_framework import serializers


class CmsNotificationSerializer(serializers.ModelSerializer):

    post_date = serializers.DateTimeField()
    notify_end_date = serializers.DateTimeField()

    def validate(self, attrs):
        """Ensure that post_date occurs before notify_end_date."""

        if attrs['post_date'] > attrs['notify_end_date']:
            raise serializers.ValidationError("Post date must occur before promotion end date.")

        return attrs

    class Meta:
        model = CmsNotification
