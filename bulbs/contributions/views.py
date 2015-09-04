"""API Views and ViewSets"""

import datetime

from django.utils import dateparse, timezone

from rest_framework import viewsets, routers, mixins
from rest_framework.settings import api_settings

from rest_framework_csv.renderers import CSVRenderer

from .models import (ContributorRole, Contribution, FreelanceProfile, LineItem, Override)
from .serializers import (ContributorRoleSerializer, ContributionReportingSerializer, ContentReportingSerializer, FreelanceProfileSerializer, LineItemSerializer, OverrideSerializer)
from bulbs.content.models import Content


class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer


class ContributorRoleViewSet(viewsets.ModelViewSet):
    queryset = ContributorRole.objects.all()
    serializer_class = ContributorRoleSerializer


class OverrideViewSet(viewsets.ModelViewSet):

    model = Override
    queryset = Override.objects.all()
    serializer_class = OverrideSerializer


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

        content = Content.objects.filter(published__range=(start_date, end_date)).prefetch_related("authors", "contributions").select_related("feature_type")

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


class FreelanceReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = FreelanceProfileSerializer

    def get_queryset(self):
        now = timezone.now()

        start_date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=now.tzinfo
        )
        if "start" in self.request.GET:
            start_date = dateparse.parse_date(self.request.GET["start"])

        end_date = now
        if "end" in self.request.GET:
            end_date = dateparse.parse_date(self.request.GET["end"])

        qs = FreelanceProfile.objects.all()

        # if start_date:
        #     qs = qs.filter(payment_date__gt=start_date)
        # if end_date:
        #     qs = qs.filter(payment_date__lt=end_date)

        return qs



api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"line-items", LineItemViewSet, base_name="line-items")
api_v1_router.register(r"role", ContributorRoleViewSet, base_name="contributorrole")
api_v1_router.register(r"rate-overrides", OverrideViewSet, base_name="rate-overrides")
api_v1_router.register(r"reporting", ReportingViewSet, base_name="contributionreporting")
api_v1_router.register(r"contentreporting", ContentReportingViewSet, base_name="contentreporting")
api_v1_router.register(r"freelancereporting", FreelanceReportingViewSet, base_name="freelancereporting")
