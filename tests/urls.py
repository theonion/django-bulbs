from bulbs.base.views import ContentListView
from testapp.models import TestContentObj, TestContentObjTwo

from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^base/', include('bulbs.base.urls')),
    url(r'^images/', include('bulbs.images.urls')),
    url(r'^content_list_one\.html', ContentListView.as_view(types=[TestContentObj], template_name="testapp/list.html"))
)
