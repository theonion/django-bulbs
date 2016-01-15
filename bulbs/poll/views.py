from django.views.decorators.cache import cache_control

from .models import Poll, Answer
from bulbs.content.views import BaseContentDetailView


class PollDetailView(BaseContentDetailView):

    model = Poll


poll_detail = cache_control(max_age=600)(PollDetailView.as_view())
