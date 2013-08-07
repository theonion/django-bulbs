from django.conf.urls import patterns, url

urlpatterns = patterns('bulbs.content.views',
    url(r'^search/tags$', 'search_tags', name='search_tags'),
    url(r'^search/feature_types$', 'search_feature_types', name='search_feature_types'),
    url(r'^(?P<pk>\d+)/tags$', 'manage_content_tags'),
)
