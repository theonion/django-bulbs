from rest_framework import viewsets
from rest_framework import filters

from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer


class PollViewSet(viewsets.ModelViewSet):
    model = Poll
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filter_backends = (filters.OrderingFilter,)


class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
