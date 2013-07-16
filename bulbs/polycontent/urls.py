from django.conf.urls import patterns, url


urlpatterns = patterns('bulbs.polycontent.views',
   url(r'^list/$', 'content_list'),
   url(r'^detail/(?P<pk>\d+)/$', 'content_detail'),
)

