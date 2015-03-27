from rest_framework import routers, viewsets, filters

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    model = Campaign
    serializer_class = CampaignSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    paginate_by = 10
    search_fields = ("campaign_label", "sponsor_name",)

api_v1_router = routers.DefaultRouter()
api_v1_router.register(
    r"campaign",
    CampaignViewSet,
    base_name="campaign")
