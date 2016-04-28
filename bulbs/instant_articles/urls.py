from django.conf.urls import patterns, url

from .views import (
    instant_article_rss, instant_article, instant_article_analytics, instant_article_ad
)

urlpatterns = patterns(
    "",
    url(r"^instant_articles/feed", instant_article_rss, name="instant_articles"),
    url(r"^instant_article/(?P<pk>\d+)/?$", instant_article, name="instant_article"),
    url(
        r"^instant_article/(?P<pk>\d+)/analytics$",
        instant_article_analytics,
        name="instant_article_analytics"
    ),
    url(r"^instant_article/(?P<pk>\d+)/ad$", instant_article_ad, name="instant_article_ad"),
)
