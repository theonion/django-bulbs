from django_filters import DateTimeFilter, FilterSet
from rest_framework import routers, viewsets, filters
from rest_framework.permissions import IsAdminUser

from .models import Campaign
from .serializers import CampaignSerializer


class CampaignFilter(FilterSet):
    start_date = DateTimeFilter(lookup_type="lte")
    end_date = DateTimeFilter(lookup_type="gt")

    class Meta(object):
        model = Campaign
        fields = ("start_date", "end_date", )


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    paginate_by = 10
    # filters
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
    filter_class = CampaignFilter
    # search
    search_fields = ("campaign_label", "sponsor_name", )
    # ordering
    ordering_fields = ("campaign_label", "sponsor_name", "start_date", "end_date", )
    permission_classes = [IsAdminUser]


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"campaign", CampaignViewSet, base_name="campaign")
