from rest_framework import routers

from bulbs.liveblog.viewsets import LiveBlogEntryViewSet

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"liveblog/entry",
    LiveBlogEntryViewSet,
    base_name="liveblog-entry"
)

urlpatterns = api_v1_router.urls
