from django.conf.urls import url, patterns

urlpatterns = patterns("bulbs.redirects.views",
    url(r"^(?P<pk>\d+)/?$", "utm_redirect"),   # noqa
    url(r"^(?P<pk>\d+)(?P<source>[a-z])(?P<medium>[a-z])(?P<name>[a-z])/?$", "utm_redirect")
)
