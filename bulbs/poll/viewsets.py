from rest_framework import viewsets

from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer


class PollViewSet(viewsets.ModelViewSet):
    model = Poll
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
