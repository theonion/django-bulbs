from rest_framework import filters, viewsets

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filters_backend = filters.DjangoFilterBackend
    paginate_by = 20
