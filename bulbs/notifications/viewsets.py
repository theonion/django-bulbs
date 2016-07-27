from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):

    queryset = Notification.objects.all().order_by('-created_on')
    serializer_class = NotificationSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter)
    filter_fields = ('is_published',)
    search_fields = ('internal_title',)
    ordering_fields = ('internal_title',
                       'is_published',
                       'created_on')
    paginate_by = 20
    permission_classes = [IsAdminUser]


class ReadOnlyNotificationViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Notification.objects.filter(is_published=True)
    serializer_class = NotificationSerializer
    paginate_by = 20
