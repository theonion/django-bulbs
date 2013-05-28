from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^base/', include('bulbs.base.urls')),
)