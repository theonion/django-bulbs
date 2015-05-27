from django.template import RequestContext
from django.utils.timezone import now
from django.views.decorators.cache import cache_control

from bulbs.content.views import ContentListView


class RSSView(ContentListView):
    """Really simply, this syndicates Content."""
    template_name = "feeds/rss.xml"
    paginate_by = 20
    feed_title = "RSS Feed"
    utm_params = "utm_medium=RSS&amp;utm_campaign=feeds"

    def get_template_names(self):
        return ["feeds/rss.xml", "feeds/_rss.xml"]

    @cache_control(max_age=600)
    def get(self, request, *args, **kwargs):
        response = super(RSSView, self).get(request, *args, **kwargs)
        response["Content-Type"] = "application/rss+xml"
        return response

    def get_queryset(self):
        return super(RSSView, self).get_queryset().full().execute()[:self.paginate_by]

    def get_context_data(self, *args, **kwargs):
        context = super(RSSView, self).get_context_data(*args, **kwargs)
        context["full"] = (self.request.GET.get("full", "false").lower() == "true")
        context["images"] = (self.request.GET.get("images", "false").lower() == "true")
        context["build_date"] = now()
        context["title"] = self.feed_title
        context["feed_url"] = self.request.build_absolute_uri()
        context["search_url"] = self.request.build_absolute_uri(
            u"/search?%s" % self.request.META["QUERY_STRING"])

        # OK, so this is kinda brutal. Stay with me here.
        for content in context["page_obj"].object_list:
            feed_path = content.get_absolute_url() + "?" + self.utm_params
            content.feed_url = self.request.build_absolute_uri(feed_path)

        return RequestContext(self.request, context)
