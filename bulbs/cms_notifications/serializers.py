from rest_framework import serializers

from bulbs.cms_notifications.models import CmsNotification


class CmsNotificationSerializer(serializers.ModelSerializer):
    """
    serializer class for `bulbs.cms_notifications.CmsNotification` model
    """

    post_date = serializers.DateTimeField()
    notify_end_date = serializers.DateTimeField()

    class Meta:
        model = CmsNotification

    def validate(self, attrs):
        """Ensure that post_date occurs before notify_end_date.

        :param attrs: `dict` of model attributes
        :return: `dict` of model attributes
        :raise: `rest_framework.serializers.ValidationError`
        """
        if attrs['post_date'] > attrs['notify_end_date']:
            raise serializers.ValidationError("Post date must occur before promotion end date.")
        return attrs
