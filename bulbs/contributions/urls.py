from django.conf.urls import url, include

from bulbs.contributions import signals  # NOQA

from .views import api_v1_router, api_v1_role_router, nested_role_router

urlpatterns = (
    url(r"^", include(api_v1_router.urls)),
    url(r"^", include(api_v1_role_router.urls)),
    url(r"^", include(nested_role_router.urls))
)
