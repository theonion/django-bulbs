from django.conf.urls import patterns, include, url

from .api import api_v1_router

urlpatterns = patterns(
    url(r"^", include(api_v1_router.urls)),
)
