from bulbs.content.views import ContentListView

from django.conf.urls import patterns, url, include


urlpatterns = patterns(
    "",
    url(r"^api/v1/", include("bulbs.api.urls")),  # noqa
    url(r"^content_list_one\.html", ContentListView.as_view(template_name="testapp/content_list.html")),
    url(r"^videos/", include("bulbs.videos.urls")),
    url(r"^r/", include("bulbs.redirects.urls")),
    url(r"^feeds", include("bulbs.feeds.urls"))
)
