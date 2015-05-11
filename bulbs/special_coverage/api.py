from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser

from .models import SpecialCoverage
from .serializers import SpecialCoverageSerializer


class SpecialCoverageViewSet(viewsets.ModelViewSet):
    queryset = SpecialCoverage.objects.all()
    serializer_class = SpecialCoverageSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, filters.DjangoFilterBackend,)
    filter_fields = ("active", "promoted")
    search_fields = (
        "name",
        "description",
        "campaign__campaign_label",
        "campaign__sponsor_name"
    )
    ordering_fields = (
        "name",
        "campaign__campaign_label",
        "campaign__sponsor_name"
    )
    paginate_by = 10
    permission_classes = [IsAdminUser]

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"special-coverage",
    SpecialCoverageViewSet,
    base_name="special-coverage")
