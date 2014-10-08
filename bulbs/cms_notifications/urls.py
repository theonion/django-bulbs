from bulbs.cms_notifications.api import api_v1_router
from django.conf.urls import url, include, patterns

urlpatterns = patterns(
    url(r"^", include(api_v1_router.urls)),
)