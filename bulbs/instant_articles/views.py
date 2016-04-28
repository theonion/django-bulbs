from bulbs.content.filters import FeatureTypes
from bulbs.content.models import Content
from bulbs.content.views import BaseContentDetailView
from bulbs.feeds.views import RSSView

from django.template import RequestContext, loader
from django.template.base import TemplateDoesNotExist
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView


class InstantArticleRSSView(RSSView):
    paginate_by = 100
    template_name = "feeds/instant_article_rss.xml"
    feed_title = "Instant Articles RSS Feed"

    def get_queryset(self):
        return Content.search_objects.instant_articles()

    def get_template_names(self):
        return ["feeds/instant_article_rss.xml"]

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
                content.instant_article_body = loader.render_to_string(
                    "instant_article/{}_instant_article.html".format(content.es_type), content_ctx
                )
            except TemplateDoesNotExist:
                content.instant_article_body = loader.render_to_string(
                    "instant_article/_instant_article.html", content_ctx
                )

        return RequestContext(self.request, context)


class InstantArticleContentView(BaseContentDetailView):

    redirect_correct_path = False

    def get_template_names(self):
        template_names = []
        template_names.append("default_instant_article.html")
        template_names.append("{}_instant_article.html".format(feature_type))
        return ["instant_article/{}_instant_article.html".format(self.object.type)]

    def get_context_data(self, *args, **kwargs):
        context = super(InstantArticleContentView, self).get_context_data(*args, **kwargs)
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
        return context

instant_article_rss = cache_control(max_age=600)(InstantArticleRSSView.as_view())
instant_article = cache_control(max_age=600)(InstantArticleContentView.as_view())
instant_article_analytics = cache_control(max_age=600)(InstantArticleAnalyticsView.as_view())
instant_article_ad = cache_control(max_age=600)(InstantArticleAdView.as_view())
