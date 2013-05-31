from django.conf.urls import patterns, url

urlpatterns = patterns('bulbs.content.views',
    url(r'^search/tags$', 'search_tags', name="search_tags"),
)
