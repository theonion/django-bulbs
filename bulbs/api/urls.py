from django.conf.urls import url, include

from .views import api_v1_router

urlpatterns = (
    url(r"^me/logout$", "django.contrib.auth.views.logout", name="logout"),
    url(r"^", include(api_v1_router.urls))       # noqa
)
