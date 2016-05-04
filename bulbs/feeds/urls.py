from django.conf.urls import url, patterns

from .views import GlanceFeedViewSet, RSSView, SpecialCoverageRSSView


urlpatterns = patterns(
    "",
    url(r"^rss", RSSView.as_view(), name="rss-feed"),
    url(r"^sc-rss", SpecialCoverageRSSView.as_view(), name="sc-rss-feed"),
    url(r"^glance.json$", GlanceFeedViewSet.as_view({'get': 'list'}), name="glance-feed"),
)
