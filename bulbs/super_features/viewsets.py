from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from bulbs.api.permissions import CanEditContent
from bulbs.utils.methods import get_query_params
from bulbs.super_features.utils import get_superfeature_model, get_superfeature_serializer


SUPERFEATURE_MODEL = get_superfeature_model()
SUPERFEATURE_SERIALIZER = get_superfeature_serializer()


class SuperFeatureViewSet(viewsets.ModelViewSet):

    model = SUPERFEATURE_MODEL
    queryset = SUPERFEATURE_MODEL.objects.filter(is_parent=True)
    serializer_class = SUPERFEATURE_SERIALIZER
    permission_classes = [IsAdminUser, CanEditContent]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ("title",)
    ordering_fields = ("title",)
    paginate_by = 20
