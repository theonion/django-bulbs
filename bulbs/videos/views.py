from django.views.decorators.cache import cache_control

import requests

from bulbs.content.views import BaseContentDetailView


class SeriesDetailView(BaseContentDetailView):
    redirect_correct_path = False

    def get_template_names(self):
        template_names = ["videos/series-detail.html"]
        return template_names

    def get(self, request, *args, **kwargs):
        parser_context = self.request.parser_context.get("kwargs", {})
        slug = parser_context.get("slug", None)

        # make request to studios
        r = requests.get(slug)

        self.data = r.json()

    # :(
    # def get_queryset(self):
    #     """Return all videos associated with a given series."""
    #     parser_context = self.request.parser_context.get("kwargs", {})
    #     series_slug = parser_context.get("series_slug", None)
    #     series = get_object_or_404(Series, slug=series_slug)
    #     return series.get_all_videos()

    def get_context_data(self, *args, **kwargs):
        context = super(SeriesDetailView, self).get_context_data()

        context["channel_name"] = self.data['channel_name']
        context["series_name"] = self.data['series_name']
        context["series_description"] = self.data['series_description']
        context["total_seasons"] = self.data['total_seasons']
        context["total_episdoes"] = self.data['total_episdoes']

        return context

series_detail = cache_control(max_age=600)(SeriesDetailView.as_view())
