from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404

from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bulbs.content.models import Content
from bulbs.recirc.serializers import RecircContentSerializer


class RecircViewSet(views.APIView):

    permission_classes = (AllowAny,)

    def get(self, request, pk):
        content = get_object_or_404(Content, id=pk)
        if not content.is_published:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RecircContentSerializer(
            content.get_recirc_content(count=3).execute(),
            many=True
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class InlineRecircViewSet(views.APIView):

    permission_classes = (AllowAny,)

    def get(self, request, pk):
        content = get_object_or_404(Content, id=pk)
        if not content.is_published:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RecircContentSerializer(
            content.get_inline_recirc_content(count=3).execute(),
            many=True
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


inline_recirc = cache_control(max_age=600)(InlineRecircViewSet.as_view())
recirc = cache_control(max_age=600)(RecircViewSet.as_view())
