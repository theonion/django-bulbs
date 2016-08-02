from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from bulbs.api.permissions import CanEditContent
from bulbs.utils.methods import get_query_params
from bulbs.super_features.utils import get_superfeature_model, get_superfeature_serializer


SUPERFEATURE_MODEL = get_superfeature_model()
SUPERFEATURE_SERIALIZER = get_superfeature_serializer()


class SuperFeatureListView(viewsets.ModelViewSet):
    # return SF objects where is_parent = True
    # option to order by title
    # ability to search/filter by title
    pass
