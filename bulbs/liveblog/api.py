from django.conf.urls import url

from rest_framework import routers

from bulbs.liveblog.viewsets import LiveBlogEntryViewSet, PublicLiveBlogEntryViewSet

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"liveblog/entry",
    LiveBlogEntryViewSet,
    base_name="liveblog-entry"
)

urlpatterns = [
    url(r"api/v1/liveblog/public/entry/?$",
        PublicLiveBlogEntryViewSet.as_view({'get': 'list'}),
        name="public-liveblog-entry"),
]

urlpatterns += api_v1_router.urls
