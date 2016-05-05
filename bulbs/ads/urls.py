from django.conf.urls import patterns, url


urlpatterns = patterns("bulbs.ads.views",
    url(r"^targeting$", "targeting", name="targeting"),  # noqa
)
