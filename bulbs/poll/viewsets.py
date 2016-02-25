from rest_framework import viewsets
from rest_framework import filters

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
    paginate_by = 20
    filter_backends = (
            filters.OrderingFilter,
            filters.SearchFilter,)
    ordering_fields = (
            "title",
            "published",
            "end_date",)
    search_fields = [
            "answers",
            "title",]

class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    permission_classes = [
        IsAdminUser,
        CanEditContent,
    ]
    serializer_class = AnswerSerializer
