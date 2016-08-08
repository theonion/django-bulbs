from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_control

from .viewsets import ReadOnlyNotificationViewSet


urlpatterns = patterns(
    "",
    url(
        r"^notifications.json",
        cache_control(max_age=300)(
            ReadOnlyNotificationViewSet.as_view({'get': 'list'})
        ), name="notification-all"),
)
