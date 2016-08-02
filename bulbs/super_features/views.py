from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from bulbs.api.permissions import CanEditContent
from bulbs.super_features.utils import get_superfeature_model, get_superfeature_partial_serializer


SUPERFEATURE_MODEL = get_superfeature_model()
SUPERFEATURE_PARTIAL_SERIALIZER = get_superfeature_partial_serializer()


class RelationViewSet(views.APIView):

    permission_classes = (IsAdminUser, CanEditContent,)

    def get(self, request, pk):
        children = SUPERFEATURE_MODEL.objects.filter(parent__id=pk)
        result = SUPERFEATURE_PARTIAL_SERIALIZER(children, many=True)

        return Response(result.data, status=status.HTTP_200_OK)
