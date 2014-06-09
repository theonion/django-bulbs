from django.conf.urls import url, patterns

from .views import RSSView


urlpatterns = patterns("",
    url(r"^rss", RSSView.as_view(), name="rss-feed")  # noqa
)
