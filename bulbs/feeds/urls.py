from django.conf.urls import url, patterns

from .views import GlanceFeedView, RSSView, SpecialCoverageRSSView


urlpatterns = patterns(
    "",
    url(r"^rss", RSSView.as_view(), name="rss-feed"),
    url(r"^sc-rss", SpecialCoverageRSSView.as_view(), name="sc-rss-feed"),
    url(r"^glance.json$", GlanceFeedView.as_view(), name="glance-feed"),
)
