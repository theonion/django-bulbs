from django.conf.urls import patterns, include, url

from bulbs.videos.api import router

urlpatterns = patterns('bulbs.videos.views',
    url(r'api/', include(router.urls)),
    url(r'videoAttrs\.js$', 'video_attrs'),
    url(r'notification$', 'notification')
)
