from django.conf.urls import url

from rest_framework import routers

from bulbs.super_features.views import (RelationViewSet,
                                        RelationOrderingViewSet,
                                        SetChildrenDatesViewSet)
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
    url(
        r'super-feature/(?P<pk>\d+)/relations/ordering/?$',
        RelationOrderingViewSet.as_view(),
        name='super-feature-relations-ordering'
    ),
    url(
        r'super-feature/(?P<pk>\d+)/set-children-dates',
        SetChildrenDatesViewSet.as_view(),
        name='super-feature-set-children-dates'
    )
]

urlpatterns += api_v1_router.urls
