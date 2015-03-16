from django.conf.urls import patterns, include, url

from .api import api_v1_router

urlpatterns = api_v1_router.urls
