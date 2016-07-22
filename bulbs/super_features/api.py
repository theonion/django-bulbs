from django.conf.urls import url

from bulbs.super_features.viewsets import RelationViewSet

urlpatterns = [
    url(
        r'content/(?P<pk>\d+)/relations/?$',
        RelationViewSet.as_view(),
        name='content-relations'
    ),
]
