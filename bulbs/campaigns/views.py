from rest_framework import routers, viewsets

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    model = Campaign
    serializer_class = CampaignSerializer


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"campaign", CampaignViewSet)
