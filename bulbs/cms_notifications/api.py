from rest_framework import viewsets

from bulbs.api.permissions import CanEditCmsNotifications
from bulbs.cms_notifications.models import CmsNotification
from bulbs.cms_notifications.serializers import CmsNotificationSerializer


class CmsNotificationsViewSet(viewsets.ModelViewSet):
    """
    viewset for `bulbs.cms_notifications.CmsNotification` model
    """

    queryset = CmsNotification.objects.all()
    serializer_class = CmsNotificationSerializer
    permission_classes = [CanEditCmsNotifications]


# defines a generic django view mapping for the CMS Notifications
notifications_view = CmsNotificationsViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'delete': 'destroy'
})
