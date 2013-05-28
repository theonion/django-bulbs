from django.conf.urls import patterns, url

urlpatterns = patterns('bulbs.base.views',
    url(r'^search/tags$', 'search_tags', name="search_tags"),
)
