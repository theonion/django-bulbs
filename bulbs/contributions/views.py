"""API Views and ViewSets"""

import datetime

from django.utils import dateparse, timezone

from elasticsearch_dsl import filter as es_filter
from rest_framework import viewsets, routers, mixins
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer
from rest_framework_nested import routers as nested_routers

from bulbs.content.filters import FeatureTypes, Published, Tags


from .filters import ESPublishedFilterBackend, StartEndFilterBackend
from .models import (
    ContributorRole, Contribution, FeatureTypeRate, FlatRate, FreelanceProfile, HourlyRate,
    LineItem, OverrideProfile, ReportContent, MANUAL
)
from .renderers import ContributionReportingRenderer
from .csv_serializers import ContributionCSVSerializer
from .serializers import (
    ContributorRoleSerializer, ContributionReportingSerializer, ContentReportingSerializer,
    FeatureTypeRateSerializer, FlatRateSerializer, FreelanceProfileSerializer,
    HourlyRateSerializer, LineItemSerializer, OverrideProfileSerializer
)
from .utils import get_forced_payment_contributions


class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
    start_fields = ("payment_date",)
    end_fields = ("payment_date",)
    filter_backends = (StartEndFilterBackend,)
    paginate_by = 20


class ContributorRoleViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorRoleSerializer

    def get_queryset(self):
        queryset = ContributorRole.objects.all()
        if self.request.QUERY_PARAMS.get("override", None) == "true":
            queryset = queryset.exclude(payment_type=MANUAL)
        return queryset


class NestedRateViewSet(viewsets.ModelViewSet):
    """filters queryset by role given the role_pk url kwarg"""

    def get_queryset(self):
        role_pk = self.request.parser_context["kwargs"].get("role_pk")
        return self.model.objects.filter(role__pk=role_pk)


class FlatRateViewSet(NestedRateViewSet):

    model = FlatRate
    serializer_class = FlatRateSerializer
    paginate_by = 20


class HourlyRateViewSet(NestedRateViewSet):

    model = HourlyRate
    serializer_class = HourlyRateSerializer
    paginate_by = 20


class FeatureTypeRateViewSet(NestedRateViewSet):

    model = FeatureTypeRate
    serializer_class = FeatureTypeRateSerializer
    paginate_by = 20


class OverrideProfileViewSet(viewsets.ModelViewSet):

    model = OverrideProfile
    queryset = OverrideProfile.search_objects.all()
    serializer_class = OverrideProfileSerializer


class ContentReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = ContentReportingSerializer
    filter_backends = (ESPublishedFilterBackend,)
    paginate_by = 20

    def get_queryset(self):
        qs = ReportContent.search_objects.search()

        # TODO: reintroduce forced submissions
        # include, exclude = get_forced_payment_contributions(start_date, end_date)
        # include_ids = include.values_list("content__id", flat=True)
        # exclude_ids = exclude.values_list("content__id", flat=True)

        # content = Content.objects.filter(
        #     contributions__gt=0
        # ).filter(
        #     published__range=(start_date, end_date)
        # ).exclude(
        #     pk__in=exclude_ids
        # ).prefetch_related(
        #     "authors", "contributions"
        # ).select_related(
        #     "feature_type"
        # ).distinct() | Content.objects.filter(pk__in=include_ids).distinct()

        if "feature_types" in self.request.QUERY_PARAMS:
            feature_types = self.request.QUERY_PARAMS.getlist("feature_types")
            qs = qs.filter(FeatureTypes(feature_types))

        if "tags" in self.request.QUERY_PARAMS:
            tags = self.request.QUERY_PARAMS.getlist("tags")
            qs = qs.filter(Tags(tags))

        # if "staff" in self.request.QUERY_PARAMS:
        #     staff = self.request.QUERY_PARAMS.get("staff")
        #     if staff == "freelance":
        #         contribution_content_ids = Contribution.objects.filter(
        #             contributor__freelanceprofile__is_freelance=True
        #         ).values_list(
        #             "content__id", flat=True
        #         ).distinct()
        #     elif staff == "staff":
        #         contribution_content_ids = Contribution.objects.filter(
        #             contributor__freelanceprofile__is_freelance=False
        #         ).values_list(
        #             "content__id", flat=True
        #         ).distinct()
        #     if contribution_content_ids:
        #         content = content.filter(pk__in=contribution_content_ids)

        if "contributors" in self.request.QUERY_PARAMS:
            contributors = self.request.QUERY_PARAMS.getlist("contributors")
            qs = qs.filter(
                es_filter.Terms(**{'contributions.contributor.username': contributors})
            )
        #     contribution_content_ids = Contribution.objects.filter(
        #         contributor__username__in=contributors
        #     ).values_list(
        #         "content__id", flat=True
        #     ).distinct()
        #     content = content.filter(pk__in=contribution_content_ids)

        return qs


class ReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (
        ContributionReportingRenderer,
    ) + tuple(
        api_settings.DEFAULT_RENDERER_CLASSES
    )
    filter_backends = (ESPublishedFilterBackend,)
    paginate_by = 20

    def list(self, request):
        format = self.request.QUERY_PARAMS.get('format', None)
        if format == 'csv':
            queryset = self.get_queryset()
            # TODO: get rid of this csv pattern so it incorporates the typical restful patterns.
            queryset = ESPublishedFilterBackend().filter_queryset(request, queryset, None)
            queryset = queryset[:queryset.count()]
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super(ReportingViewSet, self).list(request)

    def get_serializer_class(self):
        format = self.request.QUERY_PARAMS.get('format', None)
        if format == 'csv':
            return ContributionCSVSerializer
        return ContributionReportingSerializer

    def get_queryset(self):
        qs = Contribution.search_objects.search()

        feature_types = self.request.QUERY_PARAMS.getlist('feature_types')
        if feature_types:
            qs = qs.filter(
                es_filter.Terms(**{'content.feature_type.slug': feature_types})
            )

        contributors = self.request.QUERY_PARAMS.getlist('contributors')
        if contributors:
            qs = qs.filter(
                es_filter.Terms(**{'contributor.username': contributors})
            )

        tags = self.request.QUERY_PARAMS.getlist('tags')
        if tags:
            pass

        staff = self.request.QUERY_PARAMS.get('staff', None)
        if staff:
            is_freelance = True if staff == 'freelance' else False
            qs = qs.filter(
                es_filter.Term(**{'contributor.is_freelance': is_freelance})
            )
        return qs.sort('id')


class FreelanceReportingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):

    renderer_classes = (CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = FreelanceProfileSerializer
    paginate_by = 20

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
            contribution_qs = contribution_qs.filter(content__feature_type__slug__in=feature_types)

        if "tags" in self.request.QUERY_PARAMS:
            tags = self.request.QUERY_PARAMS.getlist("tags")
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

# Nested routes for roles
api_v1_role_router = nested_routers.DefaultRouter()
api_v1_role_router.register(r"role", ContributorRoleViewSet, base_name="contributorrole")
nested_role_router = nested_routers.NestedSimpleRouter(api_v1_role_router, "role", lookup="role")
nested_role_router.register("flat_rates", FlatRateViewSet, base_name="flat-rate")
nested_role_router.register("hourly_rates", HourlyRateViewSet, base_name="hourly-rate")
nested_role_router.register(
    "feature_type_rates", FeatureTypeRateViewSet, base_name="feature-type-rate"
)

api_v1_router.register(r"rate-overrides", OverrideProfileViewSet, base_name="rate-overrides")
api_v1_router.register(r"reporting", ReportingViewSet, base_name="contributionreporting")
api_v1_router.register(r"contentreporting", ContentReportingViewSet, base_name="contentreporting")
api_v1_router.register(
    r"freelancereporting", FreelanceReportingViewSet, base_name="freelancereporting"
)
