from rest_framework import viewsets
from rest_framework import filters

from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from bulbs.api.views import ContentViewSet
from bulbs.api.permissions import CanEditContent
from bulbs.utils.methods import get_query_params, get_request_data

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

    def list(self, request, *args, **kwargs):
        """Modified list view to driving listing from ES"""
        search_kwargs = {"published": False}

        for field_name in ("before", "after", "status", "published"):

            if field_name in get_query_params(self.request):
                search_kwargs[field_name] = get_query_params(self.request).get(field_name)

        if "search" in get_query_params(self.request):
            search_kwargs["query"] = get_query_params(self.request).get("search")

        queryset = self.model.search_objects.search(**search_kwargs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AnswerViewSet(viewsets.ModelViewSet):
    model = Answer
    queryset = Answer.objects.all()
    permission_classes = [
        IsAdminUser,
        CanEditContent,
    ]
    serializer_class = AnswerSerializer
