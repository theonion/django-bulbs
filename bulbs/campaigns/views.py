from datetime import datetime

from rest_framework import routers, viewsets, filters
from rest_framework.permissions import IsAdminUser

from .models import Campaign
from .serializers import CampaignSerializer

from bulbs.utils.methods import get_query_params


class CampaignActiveFilter(filters.BaseFilterBackend):
    """Checks for a value for 'active' in query parameters, filters from this
    based on start_date and end_date. 'active' as True will return campaigns
    where start_date <= now < end_date and 'active' as False will return campaigns
    where now < start_date || now >= end_date."""

    def filter_queryset(self, request, queryset, view):

        new_queryset = queryset

        key_active = 'active'

        now = datetime.now()
        if key_active in get_query_params(request):
            val = get_query_params(request)[key_active].lower()
            if val == 'true':
                # start_date <= now < end_date
                new_queryset = queryset.filter(
                    start_date__lte=now,
                    end_date__gt=now
                )
            elif val == 'false':
                # now < start_date || now >= end_date
                new_queryset = \
                    queryset.filter(start_date__gt=now) | \
                    new_queryset.filter(end_date__lte=now)

        return new_queryset


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    paginate_by = 10
    filter_backends = (
        CampaignActiveFilter,
        filters.SearchFilter,
        filters.OrderingFilter,)
    search_fields = (
        "campaign_label",
        "sponsor_name",)
    ordering_fields = (
        "campaign_label",
        "sponsor_name",
        "start_date",
        "end_date",)
    permission_classes = [IsAdminUser]


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"campaign", CampaignViewSet, base_name="campaign")
