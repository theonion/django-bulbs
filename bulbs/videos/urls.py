from django.conf.urls import patterns, url

urlpatterns = patterns(
    "",
    url(
        r"v/(?P<videohub_ref_id>\d+)/?$",
        "bulbs.videos.views.video_redirect",
        name="video_redirect"
    )
)
