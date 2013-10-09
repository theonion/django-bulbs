from django.conf.urls import patterns, url

urlpatterns = patterns('bulbs.videos.views',
    url(r'videoAttrs\.js$', 'video_attrs'),
    url(r'notification$', 'notification')
)
