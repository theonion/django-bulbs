from bulbs.content.views import ContentListView

from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^content/', include('bulbs.content.urls')),
    url(r'^images/', include('bulbs.images.urls')),
    url(r'^content_list_one\.html', ContentListView.as_view(template_name='testapp/content_list.html')),
)
