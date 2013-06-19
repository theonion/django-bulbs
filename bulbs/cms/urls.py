from django.conf.urls import url, patterns

from bulbs.cms.views import AdminListView


urlpatterns = patterns(
    'bulbs.cms.views',
    url(r'^list/', AdminListView.as_view())
)
