from bulbs.content.views import ContentListView
from bulbs.api.views import api_v1_router

from django.conf.urls import patterns, url, include


urlpatterns = patterns("",
    url(r"^api/v1/", include(api_v1_router.urls)),  # noqa
    url(r"^content_list_one\.html", ContentListView.as_view(template_name="testapp/content_list.html")),
    url(r"^videos/", include("bulbs.videos.urls")),
    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)
