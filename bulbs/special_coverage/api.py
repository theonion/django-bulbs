from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser

from .filters import SpecialCoverageFilter
from .models import SpecialCoverage
from .serializers import SpecialCoverageSerializer


class SpecialCoverageViewSet(viewsets.ModelViewSet):
    queryset = SpecialCoverage.objects.all()
    serializer_class = SpecialCoverageSerializer
    filter_backends = (
        SpecialCoverageFilter,
        filters.SearchFilter,
        filters.OrderingFilter,)
    boolean_fields = ("promoted",)
    search_fields = (
        "name",
        "description"
    )
    ordering_fields = (
        "name",
        "active",
        "promoted"
    )
    paginate_by = 10
    permission_classes = [IsAdminUser]

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"special-coverage",
    SpecialCoverageViewSet,
    base_name="special-coverage")
