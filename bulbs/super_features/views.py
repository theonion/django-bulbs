from django.shortcuts import get_object_or_404

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from bulbs.api.permissions import CanEditContent
from bulbs.super_features.utils import get_superfeature_model, get_superfeature_partial_serializer
from bulbs.super_features.serializers import BaseSuperFeatureRelationOrderingSerializer


SUPERFEATURE_MODEL = get_superfeature_model()
SUPERFEATURE_PARTIAL_SERIALIZER = get_superfeature_partial_serializer()


class RelationViewSet(views.APIView):

    permission_classes = (IsAdminUser, CanEditContent,)

    def get(self, request, pk):
        children = SUPERFEATURE_MODEL.objects.filter(parent__id=pk).order_by("ordering")
        result = SUPERFEATURE_PARTIAL_SERIALIZER(children, many=True)

        return Response(result.data, status=status.HTTP_200_OK)


class RelationOrderingViewSet(views.APIView):

    permission_classes = (IsAdminUser, CanEditContent,)

    def put(self, request, pk):
        parent = get_object_or_404(SUPERFEATURE_MODEL, pk=pk)

        serializer = BaseSuperFeatureRelationOrderingSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for item in serializer.data:
            child = get_object_or_404(SUPERFEATURE_MODEL, id=item['id'])

            if child.parent.id != parent.id:
                return Response(
                    {'detail': 'Child {} has incorrect parent'.format(child.id)},
                    status=status.HTTP_400_BAD_REQUEST)

            # NOTE: Django doesn't allow for swapping values in place,
            # so set the ordering of other object to NULL for now
            SUPERFEATURE_MODEL.objects.filter(
                parent=parent, ordering=item['ordering']
            ).update(
                ordering=None
            )

            child.ordering = item['ordering']
            child.save()

        return Response(status=status.HTTP_200_OK)


class SetChildrenDatesViewSet(views.APIView):

    permission_classes = (IsAdminUser, CanEditContent,)

    def put(self, request, pk):
        parent = get_object_or_404(SUPERFEATURE_MODEL, pk=pk)

        if not parent.published:
            return Response(
                {'detail': 'Parent publish date is not set'},
                status=status.HTTP_400_BAD_REQUEST
            )

        children = SUPERFEATURE_MODEL.objects.filter(parent__id=pk)
        for child in children:
            child.published = parent.published
            child.save()

        return Response(status=status.HTTP_200_OK)
