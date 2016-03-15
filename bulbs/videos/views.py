from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView
from django.views.decorators.cache import cache_control

import requests


class SeriesDetailView(DetailView):

    def get_template_names(self):
        template_names = ["videos/series-detail.html"]
        return template_names

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug", None)

        if not slug:
            raise Http404

        response = requests.get(settings.VIDEOHUB_BASE_URL+"/series/"+slug+".json")

        if not response.ok:
            raise Http404

        self.object = response.json()
        context = self.get_context_data()
        response = self.render_to_response(context)

        return response

    def get_context_data(self, *args, **kwargs):
        context = super(SeriesDetailView, self).get_context_data()

        context["channel_name"] = self.object['channel_name']
        context["series_name"] = self.object['series_name']
        context["series_description"] = self.object['series_description']
        context["total_seasons"] = self.object['total_seasons']
        context["total_episodes"] = self.object['total_episodes']

        return context

series_detail = cache_control(max_age=600)(SeriesDetailView.as_view())
