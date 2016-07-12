from rest_framework.routers import DefaultRouter

from bulbs.super_features.viewsets import ContentRelationViewSet


api_v1_router = DefaultRouter()
api_v1_router.register(
    r"content-relation",
    ContentRelationViewSet,
    base_name="content-relation"
)

urlpatterns = api_v1_router.urls
