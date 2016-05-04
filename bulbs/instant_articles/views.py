from django.template import RequestContext, loader
from django.template.base import TemplateDoesNotExist
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from bulbs.content.models import Content
from bulbs.content.views import BaseContentDetailView
from bulbs.feeds.views import RSSView


class InstantArticleRSSView(RSSView):
    paginate_by = 100
    template_name = "feeds/instant_article_rss.xml"
    feed_title = "Instant Articles RSS Feed"

    def get_queryset(self):
        return Content.search_objects.instant_articles()

    def get_template_names(self):
        return [
            "feeds/instant_article_rss.xml",
            "instant_article/base_instant_article_rss.xml"
        ]

    def get_context_data(self, *args, **kwargs):
        context = super(InstantArticleRSSView, self).get_context_data(*args, **kwargs)
        context["title"] = self.feed_title
        context["search_url"] = self.request.build_absolute_uri("/")

        for content in context["page_obj"].object_list:
            content.feed_url = self.request.build_absolute_uri(content.get_absolute_url())
            content_ctx = {
                "content": content,
                "absolute_uri": self.request.META.get('HTTP_HOST', None)
            }
            try:
                content.instant_article_html = loader.render_to_string(
                    "instant_article/_instant_article.html", content_ctx
                )
            except TemplateDoesNotExist:
                content.instant_article_html = loader.render_to_string(
                    "instant_article/base_instant_article.html", content_ctx
                )
        return RequestContext(self.request, context)


class InstantArticleContentView(BaseContentDetailView):

    redirect_correct_path = False

    def get_template_names(self):
        return [
            "instant_article/_instant_article.html",
            "instant_article/base_instant_article.html"
        ]

    def get_context_data(self, *args, **kwargs):
        context = super(InstantArticleContentView, self).get_context_data(*args, **kwargs)
        targeting = self.object.get_targeting()
        context["targeting"] = targeting
        context["targeting_params"] = "&".join(
            ["{}={}".format(key, value) for key, value in targeting.items()]
        )
        context["absolute_uri"] = self.request.META.get("HTTP_HOST", None)
        return context


class InstantArticleAdView(TemplateView):
    template_name = "instant_article/_instant_article_ad.html"


class InstantArticleAnalyticsView(TemplateView):
    template_name = "core/_analytics.html"

    def get_context_data(self, *args, **kwargs):
        context = {
            "fire_pageview": True,
            "platform": "Instant Articles"
        }
        context["path"] = self.request.GET.get("path", "")
        context["targeting"] = {
            "dfp_site": self.request.GET.get("dfp_site", ""),
            "dfp_feature": self.request.GET.get("dfp_feature", ""),
            "dfp_contentid": self.request.GET.get("dfp_contentid", ""),
            "dfp_pagetype": self.request.GET.get("dfp_pagetype", ""),
            "dfp_slug": self.request.GET.get("dfp_slug", "")
        }
        return context


instant_article_rss = cache_control(max_age=600)(InstantArticleRSSView.as_view())
instant_article = cache_control(max_age=600)(InstantArticleContentView.as_view())
instant_article_analytics = cache_control(max_age=600)(InstantArticleAnalyticsView.as_view())
instant_article_ad = cache_control(max_age=600)(InstantArticleAdView.as_view())
