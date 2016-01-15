from django.conf import settings
from django.conf.urls import patterns, include, url

from .routers import router


API_ROUTE = getattr(settings, 'API_ROUTE', r'api/')

poll_patterns = patterns(
    "",
    url(API_ROUTE, include(router.urls)),
)

urlpatterns = patterns(
    "bulbs.poll.views",

    url(
        r'^poll/(?P<slug>[\w-]+)-(?P<pk>\d+)/?$', 'poll_detail', name='poll-detail'
    ),
)
