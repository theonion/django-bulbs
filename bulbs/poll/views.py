import json

from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.generic.detail import DetailView

from bulbs.content.views import BaseContentDetailView
from bulbs.poll.models import Poll
from bulbs.poll.serializers import PollPublicSerializer


class PollDetailView(BaseContentDetailView):
    model = Poll
    ordering_fields = "__all__"


class MergedPollDataView(DetailView):
    model = Poll

    def render_to_response(self, context, **response_kwargs):
        """
        This endpoint sets very permiscuous CORS headers.

        Access-Control-Allow-Origin is set to the request Origin. This allows
          a page from ANY domain to make a request to this endpoint.

        Access-Control-Allow-Credentials is set to true. This allows requesting
          poll data in our authenticated test/staff environments.

        This particular combination of headers means this endpoint is a potential
            CSRF target.

        This enpoint MUST NOT write data. And it MUST NOT return any sensitive data.
        """
        serializer = PollPublicSerializer(self.object)
        response = HttpResponse(
            json.dumps(serializer.data),
            content_type="application/json"
        )
        if "HTTP_ORIGIN" in self.request.META:
            response["Access-Control-Allow-Origin"] = self.request.META["HTTP_ORIGIN"]
            response["Access-Control-Allow-Credentials"] = 'true'

        return response

poll_detail = cache_control(max_age=600)(PollDetailView.as_view())
get_merged_poll_data = cache_control(max_age=600)(MergedPollDataView.as_view())
