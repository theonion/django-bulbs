from django.conf.urls import url, include

from .views import api_v1_router, MeViewSet

urlpatterns = (
    url(r"^me/logout$", "django.contrib.auth.views.logout", name="logout"),
    url(r'^me', MeViewSet.as_view({'get': 'retrieve'}), name='me'),
    url(r"^", include(api_v1_router.urls))       # noqa
)
