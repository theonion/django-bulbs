from django.conf.urls import url, patterns
from django.views.decorators.cache import cache_control

from .views import GlanceFeedViewSet, RSSView, SpecialCoverageRSSView


urlpatterns = patterns(
    "",
    url(r"^rss", cache_control(max_age=300)(RSSView.as_view()),
        name="rss-feed"),
    url(r"^sc-rss", cache_control(max_age=300)(SpecialCoverageRSSView.as_view()),
        name="sc-rss-feed"),
    url(r"^glance.json$", cache_control(max_age=300)(GlanceFeedViewSet.as_view({'get': 'list'})),
        name="glance-feed"),
)
