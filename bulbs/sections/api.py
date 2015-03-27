from rest_framework import filters, routers, viewsets
from rest_framework.permissions import IsAdminUser

from .models import Section
from .serializers import SectionSerializer


class SectionViewSet(viewsets.ModelViewSet):
    model = Section
    serializer_class = SectionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "description")
    paginate_by = 10
    permission_classes = [IsAdminUser]

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"section",
    SectionViewSet,
    base_name="section")
