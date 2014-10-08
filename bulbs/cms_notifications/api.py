from bulbs.cms_notifications.models import CmsNotification
from bulbs.cms_notifications.serializers import CmsNotificationSerializer
from rest_framework import viewsets


class CmsNotificationsViewSet(viewsets.ModelViewSet):

    queryset = CmsNotification.objects.all()
    serializer_class = CmsNotificationSerializer


notifications_view = CmsNotificationsViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update'
})
