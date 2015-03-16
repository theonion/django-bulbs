from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser

from .models import SpecialCoverage
from .serializers import SpecialCoverageSerializer


class SpecialCoverageViewSet(viewsets.ModelViewSet):
    model = SpecialCoverage
    serializer_class = SpecialCoverageSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "description")
    paginate_by = 10
    permission_classes = [IsAdminUser]

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"special-coverage",
    SpecialCoverageViewSet,
    base_name="special-coverage")
