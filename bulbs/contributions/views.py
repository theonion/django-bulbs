"""API Views and ViewSets"""

import datetime

from django.utils import dateparse, timezone

from bulbs.content.models import Content

from rest_framework import viewsets, routers, mixins
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer

from .models import (ContributorRole, Contribution, FreelanceProfile, LineItem, OverrideProfile)
from .renderers import ContributionReportingRenderer
from .csv_serializers import ContributionCSVSerializer
from .serializers import (
    ContributorRoleSerializer, ContributionReportingSerializer, ContentReportingSerializer,
    FreelanceProfileSerializer, LineItemSerializer, OverrideProfileSerializer
)
from .utils import get_forced_payment_contributions


class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer


class ContributorRoleViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorRoleSerializer

    def get_queryset(self):
        qs = ContributorRole.objects.all()
        if self.request.QUERY_PARAMS.get('override', None) == 'true':
            qs = qs.exclude(payment_type=3)
        return qs


class OverrideProfileViewSet(viewsets.ModelViewSet):

    model = OverrideProfile
    queryset = OverrideProfile.objects.all()
    serializer_class = OverrideProfileSerializer


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
        if "end" in self.request.GET and "published" not in self.request.QUERY_PARAMS:
            end_date = dateparse.parse_date(self.request.GET["end"])

        include, exclude = get_forced_payment_contributions(start_date, end_date)
        include_ids = include.values_list("content__id", flat=True)
        exclude_ids = exclude.values_list("content__id", flat=True)
        content = Content.objects.filter(
            contributions__gt=0
        ).filter(
            published__range=(start_date, end_date)
        ).exclude(
            pk__in=exclude_ids
        ).prefetch_related(
            "authors", "contributions"
        ).select_related(
            "feature_type"
        ).distinct() | Content.objects.filter(pk__in=include_ids).distinct()

        if "feature_types" in self.request.QUERY_PARAMS:
            feature_types = self.request.QUERY_PARAMS.getlist("feature_types")
            content = content.filter(feature_type__slug__in=feature_types)

        if "tags" in self.request.QUERY_PARAMS:
            tags = self.request.QUERY_PARAMS.getlist("tags")
            content = content.filter(tags__slug__in=tags)

        if "staff" in self.request.QUERY_PARAMS:
            staff = self.request.QUERY_PARAMS.get("staff")
            if staff == "freelance":
                contribution_content_ids = Contribution.objects.filter(
                    contributor__freelanceprofile__is_freelance=True
                ).values_list(
                    "content__id", flat=True
                ).distinct()
            elif staff == "staff":
                contribution_content_ids = Contribution.objects.filter(
                    contributor__freelanceprofile__is_freelance=False
                ).values_list(
                    "content__id", flat=True
                ).distinct()
            if contribution_content_ids:
                content = content.filter(pk__in=contribution_content_ids)

        if "contributors" in self.request.QUERY_PARAMS:
            contributors = self.request.QUERY_PARAMS.getlist("contributors")
            contribution_content_ids = Contribution.objects.filter(
                contributor__username__in=contributors
            ).values_list(
                "content__id", flat=True
            ).distinct()
            content = content.filter(pk__in=contribution_content_ids)

        return content


class ReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (
        ContributionReportingRenderer,
    ) + tuple(
        api_settings.DEFAULT_RENDERER_CLASSES
    )

    def get_serializer_class(self):
        format = self.request.QUERY_PARAMS.get('format', None)
        if format == 'csv':
            return ContributionCSVSerializer
        return ContributionReportingSerializer

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
        if "feature_types" in self.request.QUERY_PARAMS:
            feature_types = self.request.QUERY_PARAMS.getlist("feature_types")
            content = content.filter(feature_type__slug__in=feature_types)

        if "tags" in self.request.QUERY_PARAMS:
            tags = self.request.QUERY_PARAMS.getlist("tags")
            content = content.filter(tags__slug__in=tags)

        content_ids = content.values_list("pk", flat=True)
        contributions = Contribution.objects.filter(content__in=content_ids)

        include, exclude = get_forced_payment_contributions(start_date, end_date, qs=contributions)
        include_ids = include.values_list('pk', flat=True).distinct()
        exclude_ids = exclude.values_list('pk', flat=True).distinct()

        contributions = contributions.exclude(
            pk__in=exclude_ids
        ) | Contribution.objects.filter(
            pk__in=include_ids
        )

        if "contributors" in self.request.QUERY_PARAMS:
            contributors = self.request.QUERY_PARAMS.getlist("contributors")
            contributions = contributions.filter(contributor__username__in=contributors)

        if "staff" in self.request.QUERY_PARAMS:
            staff = self.request.QUERY_PARAMS.get("staff")
            if staff == "freelance":
                contributions = contributions.filter(
                    contributor__freelanceprofile__is_freelance=True
                )
            elif staff == "staff":
                contributions = contributions.filter(
                    contributor__freelanceprofile__is_freelance=False
                )

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

        contribution_qs = Contribution.objects.all()

        if "feature_types" in self.request.QUERY_PARAMS:
            feature_types = self.request.QUERY_PARAMS.getlist("feature_types")
            # content = content.filter(feature_type__slug__in=feature_types)
            contribution_qs = contribution_qs.filter(content__feature_type__slug__in=feature_types)

        if "tags" in self.request.QUERY_PARAMS:
            tags = self.request.QUERY_PARAMS.getlist("tags")
            # content = content.filter(tags__slug__in=tags)
            contribution_qs = contribution_qs.filter(content__tags__slug__in=tags)

        include, exclude = get_forced_payment_contributions(
            start_date, end_date, qs=contribution_qs
        )
        include_ids = include.values_list('pk', flat=True).distinct()
        exclude_ids = exclude.values_list('pk', flat=True).distinct()

        contribution_qs = contribution_qs.filter(
            content__published__range=(start_date, end_date)
        ) | Contribution.objects.filter(
            pk__in=include_ids
        )
        contribution_qs = contribution_qs.exclude(pk__in=exclude_ids).distinct()

        if "contributors" in self.request.QUERY_PARAMS:
            contributors = self.request.QUERY_PARAMS.getlist("contributors")
            contribution_qs = contribution_qs.filter(contributor__username__in=contributors)

        contributor_ids = contribution_qs.values_list('contributor', flat=True).distinct()
        qs = FreelanceProfile.objects.filter(contributor__in=contributor_ids)

        if "staff" in self.request.QUERY_PARAMS:
            staff = self.request.QUERY_PARAMS.get("staff")
            if staff == "freelance":
                qs = qs.filter(is_freelance=True)
            elif staff == "staff":
                qs = qs.filter(is_freelance=False)
        return qs


api_v1_router = routers.DefaultRouter()
api_v1_router.register(r"line-items", LineItemViewSet, base_name="line-items")
api_v1_router.register(r"role", ContributorRoleViewSet, base_name="contributorrole")
api_v1_router.register(r"rate-overrides", OverrideProfileViewSet, base_name="rate-overrides")
api_v1_router.register(r"reporting", ReportingViewSet, base_name="contributionreporting")
api_v1_router.register(r"contentreporting", ContentReportingViewSet, base_name="contentreporting")
api_v1_router.register(
    r"freelancereporting", FreelanceReportingViewSet, base_name="freelancereporting"
)
