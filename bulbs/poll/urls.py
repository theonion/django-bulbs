from django.conf.urls import url, patterns

from bulbs.poll.views import get_merged_poll_data

urlpatterns = patterns(
    "",
    url(r"^poll/(?P<pk>[\d]+)/merged\.json$", get_merged_poll_data, name='get-merged-poll-data')
)
