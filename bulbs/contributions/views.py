"""API Views and ViewSets"""

import datetime

from django.utils import dateparse, timezone

from rest_framework import viewsets, routers, mixins
from rest_framework.settings import api_settings

from rest_framework_csv.renderers import CSVRenderer

from .models import ContributorRole, Contribution
from .serializers import ContributorRoleSerializer, ContributionReportingSerializer, ContentReportingSerializer
from bulbs.content.models import Content


class ContributorRoleViewSet(viewsets.ModelViewSet):
    queryset = ContributorRole.objects.all()
    serializer_class = ContributorRoleSerializer


class ContentReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = ContentReportingSerializer

    def get_queryset(self):
        now = timezone.now()

        start_date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=now.tzinfo)
        if "start" in self.request.GET:
            start_date = dateparse.parse_date(self.request.GET["start"])

        end_date = now
        if "end" in self.request.GET:
            end_date = dateparse.parse_date(self.request.GET["end"])

        content = Content.objects.filter(published__range=(start_date, end_date)).prefetch_related("authors", "contribution_set").select_related("feature_type")

        return content


class ReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = ContributionReportingSerializer

    def get_queryset(self):
        now = timezone.now()

        start_date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=now.tzinfo)
        if "start" in self.request.GET:
            start_date = dateparse.parse_date(self.request.GET["start"])

        end_date = now
        if "end" in self.request.GET:
            end_date = dateparse.parse_date(self.request.GET["end"])

        content = Content.objects.filter(published__range=(start_date, end_date))
        content_ids = content.values_list("pk", flat=True)
        contributions = Contribution.objects.filter(content__in=content_ids)

        ordering = self.request.GET.get("ordering", "content")
        order_options = {
            "content": "content__published",
            "user": "contributor__id"
        }
        return contributions.order_by(order_options[ordering])


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"role", ContributorRoleViewSet, base_name="contributorrole")
api_v1_router.register(r"reporting", ReportingViewSet, base_name="contributionreporting")
api_v1_router.register(r"contentreporting", ContentReportingViewSet, base_name="contentreporting")
