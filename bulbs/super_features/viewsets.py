from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from bulbs.api.permissions import CanEditContent
from bulbs.super_features.models import ContentRelation
from bulbs.super_features.serializers import ContentRelationSerializer
from bulbs.super_features.utils import get_superfeature_model, get_superfeature_partial_serializer


SUPERFEATURE_MODEL = get_superfeature_model()
SUPERFEATURE_PARTIAL_SERIALIZER = get_superfeature_partial_serializer()


class ContentRelationViewSet(viewsets.ModelViewSet):

    model = ContentRelation
    serializer_class = ContentRelationSerializer
    permission_classes = (IsAdminUser, CanEditContent,)


class RelationViewSet(views.APIView):

    permission_classes = (IsAdminUser, CanEditContent,)

    def get(self, request, pk):
        child_ids = ContentRelation.objects.filter(
                parent_id=pk
            ).values_list(
                'child_id', flat=True
            ).order_by('ordering')
        children = SUPERFEATURE_MODEL.objects.filter(id__in=child_ids)
        result = SUPERFEATURE_PARTIAL_SERIALIZER(children, many=True)

        return Response(result.data, status=status.HTTP_200_OK)
