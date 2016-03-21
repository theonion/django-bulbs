from django.views.decorators.cache import cache_control

from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class RecircViewSet(views.APIView):

    permission_classes = (AllowAny,)

    def get(self, request, pk):
        return Response(status=status.HTTP_200_OK)

recirc = cache_control(max_age=600)(RecircViewSet.as_view())
