from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control
from django.views.generic.detail import DetailView
import json

from bulbs.content.views import BaseContentDetailView
from bulbs.poll.models import Poll, Answer
from bulbs.poll.serializers import PollPublicSerializer

class PollDetailView(BaseContentDetailView):
    model = Poll

class MergedPollDataView(DetailView):
    model = Poll

    def render_to_response(self, context, **response_kwargs):
        serializer = PollPublicSerializer(self.object)
        response = HttpResponse(json.dumps(serializer.data),
            content_type="application/json"
        )
        if "HTTP_ORIGIN" in self.request.META:
            response["Access-Control-Allow-Origin"] = self.request.META["HTTP_ORIGIN"]
            response["Access-Control-Allow-Credentials"] = 'true'

        return response

poll_detail = cache_control(max_age=600)(PollDetailView.as_view())
get_merged_poll_data = cache_control(max_age=600)(MergedPollDataView.as_view())
