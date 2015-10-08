from django.conf.urls import url, patterns

from .views import RSSView, SpecialCoverageRSSView


urlpatterns = patterns("",
    url(r"^rss", RSSView.as_view(), name="rss-feed"),  # noqa
    url(r"^sc-rss", SpecialCoverageRSSView.as_view(), name="sc-rss-feed")  # noqa
)
