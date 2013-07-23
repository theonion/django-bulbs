from bulbs.content.views import ContentListView
from testapp.models import TestContentObj

from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^content/', include('bulbs.content.urls')),
    url(r'^images/', include('bulbs.images.urls')),
    url(r'^content_list_one\.html', 'testapp.views.content_list'),
    #url(r'^detail/(?P<pk>\d+)/$', 'bulbs.content.views.content_detail'),
)
