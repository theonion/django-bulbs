from django.conf.urls import url

from rest_framework import routers

from bulbs.super_features.views import RelationViewSet
from bulbs.super_features.viewsets import SuperFeatureViewSet

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"super-feature",
    SuperFeatureViewSet,
    base_name="super-feature"
)

urlpatterns = [
    url(
        r'super-feature/(?P<pk>\d+)/relations/?$',
        RelationViewSet.as_view(),
        name='super-feature-relations'
    ),
]

urlpatterns += api_v1_router.urls
