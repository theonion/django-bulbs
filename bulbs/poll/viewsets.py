from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from bulbs.api.permissions import CanEditContent
from bulbs.utils.methods import get_query_params
from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer


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

    class Meta:
        exclude = ('thumbnail_override',)

    def list(self, request, *args, **kwargs):
        """Modified list view to driving listing from ES"""
        search_kwargs = {"published": False}

        query_params = get_query_params(self.request)

        for field_name in ("status"):
            if field_name in query_params:
                search_kwargs[field_name] = query_params.get(field_name)

        if "search" in query_params:
            search_kwargs["query"] = query_params.get("search")

        # active/closed are semantics of the Poll model
        # active is analagous to 'published' in Content
        # closed is in relation to the end_date of a Poll
        if "active" in query_params:
            del search_kwargs["published"]
            search_kwargs["active"] = True

        if "closed" in query_params:
            del search_kwargs["published"]
            search_kwargs["closed"] = True

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
