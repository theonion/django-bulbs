from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from bulbs.super_features.viewsets import ContentRelationViewSet, RelationViewSet


api_v1_router = DefaultRouter()
api_v1_router.register(
    r"content-relation",
    ContentRelationViewSet,
    base_name="content-relation"
)
api_v1_router.register(
    r"relations",
    RelationViewSet,
    base_name="relations"
)

urlpatterns = [
    url(
        r'content/(?P<pk>\d+)/relations/?$',
        RelationViewSet.as_view(),
        name='content-relations'
    ),
]

urlpatterns += api_v1_router.urls
