from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from bulbs.api.permissions import CanEditContent
from bulbs.super_features.models import ContentRelation
from bulbs.super_features.serializers import ContentRelationSerializer


class ContentRelationViewSet(viewsets.ModelViewSet):

    model = ContentRelation
    serializer_class = ContentRelationSerializer
    permission_classes = (IsAdminUser, CanEditContent,)
