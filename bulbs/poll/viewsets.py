from rest_framework import viewsets

from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer

from rest_framework.permissions import IsAdminUser
from bulbs.api.views import ContentViewSet
from bulbs.api.permissions import CanEditContent

class PollViewSet(viewsets.ModelViewSet):
    model = Poll
    queryset = Poll.objects.all()
    permission_classes = [
        IsAdminUser,
        CanEditContent,
    ]
    serializer_class = PollSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    permission_classes = [
        IsAdminUser,
        CanEditContent,
    ]
    serializer_class = AnswerSerializer
