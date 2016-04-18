from collections import OrderedDict
import datetime
import six

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import dateparse, timezone

from rest_framework import serializers
from rest_framework.utils import model_meta

from bulbs.content.models import Content, FeatureType
from bulbs.content.serializers import FeatureTypeField, UserSerializer

from .models import (
    Contribution, ContributorRole, ContributionOverride, HourlyRate, FlatRate, ManualRate,
    FeatureTypeRate, FeatureTypeOverride, LineItem, OverrideProfile, Rate,
    RATE_PAYMENT_TYPES, MANUAL
)


class PaymentTypeField(serializers.Field):
    """
    payment type objects serialized to/from label/identifer
    """
    def to_representation(self, obj):
        data = dict(RATE_PAYMENT_TYPES)[obj]
        return data

    def to_internal_value(self, data):
        if isinstance(data, int):
            return data
        return dict((label, value) for value, label in RATE_PAYMENT_TYPES)[data]


class ContributorSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "full_name")

    def get_full_name(self, contributor):
        if hasattr(contributor, "get_full_name"):
            return contributor.get_full_name()
        elif hasattr(contributor, "full_name"):
            return contributor.full_name
        else:
            return contributor.first_name + " " + contributor.last_name


class ContributorField(serializers.Field):

    def to_representation(self, obj):
        return ContributorSerializer(obj).data

    def to_internal_value(self, data):
        contributor_cls = get_user_model()

        if isinstance(data, six.text_type) and data.isdigit():
            data = int(data)

        if isinstance(data, int):
            return contributor_cls.objects.get(id=data)
        elif isinstance(data, dict):
            id = data.get("id", None)
            if id is not None:
                return contributor_cls.objects.get(id=id)
        return None


class FreelanceProfileSerializer(serializers.Serializer):

    contributor = ContributorField()
    payment_date = serializers.SerializerMethodField()
    pay = serializers.SerializerMethodField()
    contributions_count = serializers.SerializerMethodField("get_contribution_count")

    def get_pay(self, obj):
        return obj.get_pay()

    def get_payment_date(self, obj):
        now = timezone.now()
        month = now.month + 1
        year = now.year
        if month > 12:
            month = 1
            year += 1
        next_payment = datetime.datetime(
            day=1,
            month=month,
            year=year,
            tzinfo=now.tzinfo
        )
        return next_payment.isoformat()

    def get_contribution_count(self, obj):
        return obj.contributor.contributions.count()


class LineItemSerializer(serializers.ModelSerializer):

    contributor = ContributorField()
    payment_date = serializers.DateTimeField()

    class Meta:
        model = LineItem


class RateSerializer(serializers.ModelSerializer):

    name = PaymentTypeField()

    class Meta:
        model = Rate


class NestedRateSerializer(serializers.ModelSerializer):
    """
    ModelSerializer that lookups the user role from the url kwargs.
    """
    def create(self, validated_data):
        lookup_kwargs = self.context["request"].parser_context["kwargs"]
        role_pk = lookup_kwargs.get("role_pk", 0)
        validated_data["role"] = get_object_or_404(ContributorRole, pk=role_pk)
        return super(NestedRateSerializer, self).create(validated_data)


class FlatRateSerializer(NestedRateSerializer):

    class Meta:
        model = FlatRate
        fields = ("id", "rate")


class HourlyRateSerializer(NestedRateSerializer):

    class Meta:
        model = HourlyRate
        fields = ("id", "rate")


class FeatureTypeRateSerializer(NestedRateSerializer):

    feature_type = FeatureTypeField(queryset=FeatureType.objects.all())

    class Meta:
        model = FeatureTypeRate
        fields = ("id", "rate", "feature_type")


class RateField(serializers.Field):
    """
    Returns the appropriate rate to represent
    Creates a new rate
    """
    def get_attribute(self, obj):
        return obj.get_rate()

    def to_representation(self, obj):
        return RateSerializer(obj).data

    def to_internal_value(self, data):
        name = data.get('name', None)
        if name:
            data['name'] = dict((label, value) for value, label in RATE_PAYMENT_TYPES)[name]
        if 'role' in data:
            rate = FlatRate(**data)
        elif 'contribution' in data:
            data["name"] = MANUAL
            rate = ManualRate(**data)
        elif 'feature_type' in data:
            rate = FeatureTypeRate(**data)
        else:
            rate = Rate(**data)
        rate.save()
        return rate


class OverrideRateField(serializers.Field):

    def get_attribute(self, obj):
        return obj.override_flatrate.first()

    def to_representation(self, obj):
        return obj.rate


class OverrideFeatureTypesField(serializers.Field):

    def get_attribute(self, obj):
        return obj.override_feature_type.all()

    def to_representation(self, obj):
        marshaller = []
        for rate in obj:
            marshaller.append({
                'feature_type': rate.feature_type.name,
                'rate': rate.rate
            })
        return marshaller


class ContributorRoleSerializer(serializers.ModelSerializer):

    payment_type = PaymentTypeField()
    rate = serializers.SerializerMethodField()

    class Meta:
        model = ContributorRole

    def get_rate(self, obj):
        rate = obj.get_rate()
        if rate:
            return rate.rate
        return None


class RoleField(serializers.Field):

    def get_attribute(self, obj):
        return (obj.role, obj)

    def to_representation(self, obj):
        obj, contribution = obj
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "payment_type": PaymentTypeField().to_representation(obj.payment_type)
        }

        if isinstance(contribution, Contribution):
            rate = data.get("rate")
            if not rate:
                rate = contribution.get_rate()
                if rate and hasattr(rate, "rate"):
                    data["rate"] = rate.rate

            # TODO: Need to separate these rate requests to a different endpoint
            content = getattr(contribution, 'content', None)
            if content is not None:

                data["rates"] = {}

                # TODO: This is redundant, but we need to lower the feature_type query on partial.
                flat_rate = FlatRate.objects.filter(role=obj).order_by("-updated_on").first()
                if flat_rate:
                    data["rates"]["flat_rate"] = {
                        "rate": flat_rate.rate,
                        "updated_on": flat_rate.updated_on.isoformat()
                    }

                hourly = HourlyRate.objects.filter(role=obj).order_by("-updated_on").first()
                if hourly:
                    data["rates"]["hourly"] = {
                        "rate": hourly.rate,
                        "updated_on": hourly.updated_on.isoformat()
                    }

                feature_type_rates = FeatureTypeRate.objects.filter(
                    role=obj, feature_type=content.feature_type
                )
                if feature_type_rates.exists():
                    ft = feature_type_rates.order_by("-updated_on")[0]
                    data["rates"]["feature_type"] = [{
                        "feature_type": ft.feature_type.name,
                        "rate": ft.rate,
                        "updated_on": ft.updated_on.isoformat()
                    }]
        return data

    def to_internal_value(self, data):
        if isinstance(data, int):
            return ContributorRole.objects.get(id=data)
        elif isinstance(data, dict):
            id = data.get("id", None)
            return ContributorRole.objects.get(id=id)
        return None


class FeatureTypeOverrideSerializer(serializers.ModelSerializer):

    rate = serializers.IntegerField(required=False)
    feature_type = FeatureTypeField(queryset=FeatureType.objects.all())

    class Meta:
        model = FeatureTypeOverride


class OverrideProfileSerializer(serializers.ModelSerializer):

    contributor = ContributorField()
    role = RoleField()
    rate = OverrideRateField(read_only=True)
    feature_types = OverrideFeatureTypesField(read_only=True)

    class Meta:
        model = OverrideProfile

    def update_feature_type_overrides(self, profile, feature_types):
        for data in feature_types:
            ft_data = data.get('feature_type', None)
            if ft_data:
                feature_type = FeatureTypeField(read_only=True).to_internal_value(
                    ft_data
                )
                rate = int(data.get('rate', 0))

                ft_override = profile.override_feature_type.get_or_create(
                    feature_type=feature_type,
                )[0]
                if ft_override.rate != rate:
                    ft_override.rate = rate
                    ft_override.save()

    def to_internal_value(self, data):
        rate = data.pop("rate", None)
        feature_types = data.pop("feature_types", None)
        override = super(OverrideProfileSerializer, self).to_internal_value(data)
        if feature_types:
            override['feature_types'] = feature_types
        if rate:
            override['rate'] = rate
        return override

    def create(self, validated_data):
        rate = validated_data.pop('rate', None)
        feature_types = validated_data.pop('feature_types', [])
        profile = super(OverrideProfileSerializer, self).create(validated_data)

        if rate or rate == 0:
            profile.override_flatrate.create(rate=rate)

        if feature_types:
            self.update_feature_type_overrides(profile, feature_types)

        return profile

    def update(self, instance, validated_data):
        rate = validated_data.pop('rate', None)
        feature_types = validated_data.pop('feature_types', [])
        profile = super(OverrideProfileSerializer, self).update(instance, validated_data)

        if rate or rate == 0:
            profile.override_flatrate.create(rate=rate)

        if feature_types:
            self.update_feature_type_overrides(profile, feature_types)

        return profile


class ContributionListSerializer(serializers.ListSerializer):

    contributor = UserSerializer()

    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        contribution_mapping = {c.id: c for c in instance}
        data_mapping = {item['id']: item for item in validated_data if "id" in item}

        # Perform creations and updates.
        ret = []
        for data in validated_data:
            contribution = None
            if "id" in data:
                contribution = contribution_mapping.get(data["id"], None)

            if contribution is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(contribution, data))

        # Perform deletions.
        for contribution_id, contribution in contribution_mapping.items():
            if contribution_id not in data_mapping:
                contribution.delete()

        return ret


class ContributionOverrideField(serializers.Field):

    def get_attribute(self, obj):
        return obj.override_contribution.first()

    def to_representation(self, obj):
        if obj:
            return obj.rate


class ContributionSerializer(serializers.ModelSerializer):

    contributor = UserSerializer()
    rate = RateField(required=False)
    role = RoleField()
    override_rate = ContributionOverrideField(read_only=True)
    content = serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())

    class Meta:
        model = Contribution
        list_serializer_class = ContributionListSerializer

    def get_rate(self, obj):
        rate = obj.get_rate()
        if not rate:
            return None
        return RateSerializer(rate).data

    def to_internal_value(self, data):
        rate_data = data.pop('rate', None)
        override_rate_data = data.pop("override_rate", None)
        data = super(ContributionSerializer, self).to_internal_value(data)
        if rate_data:
            data['rate'] = rate_data
        if override_rate_data:
            data["override_rate"] = override_rate_data
        return data

    def create(self, validated_data):
        model_cls = self.Meta.model
        info = model_meta.get_field_info(model_cls)
        many_to_many = {}
        rate_data = validated_data.pop('rate', None)
        override_rate_data = validated_data.pop("override_rate", None)
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)
        contribution = model_cls.objects.create(**validated_data)
        if rate_data:
            if isinstance(rate_data, int):
                rate_data = {"rate": rate_data}
            if isinstance(rate_data, six.text_type) or isinstance(rate_data, str):
                if rate_data.isdigit():
                    rate_data = {"rate": int(rate_data)}
            rate_data["contribution"] = contribution
            RateField().to_internal_value(rate_data)
        if override_rate_data:
            ContributionOverride.objects.create(
                contribution=contribution,
                rate=override_rate_data
            )
        return contribution


class ContributionReportingSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    pay = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Contribution
        fields = ("id", "content", "user", "pay", "role", "rate", "notes")

    def get_content(self, obj):
        return OrderedDict([
            ("id", obj.content.id),
            ("title", obj.content.title),
            ("url", obj.content.get_absolute_url()),
            ("content_type", obj.content.__class__.__name__),
            ("feature_type", getattr(obj.content.feature_type, "name", None)),
            ("published", timezone.localtime(obj.content.published))
        ])

    def get_user(self, obj):
        full_name = obj.contributor.get_full_name()
        data = {
            "id": obj.contributor.id,
            "username": obj.contributor.username,
            "full_name": full_name,
            "payroll_name": full_name
        }
        profile = getattr(obj.contributor, "freelanceprofile", None)
        if profile:
            payroll_name = getattr(profile, "payroll_name")
            if payroll_name:
                data["payroll_name"] = payroll_name
        return data

    def get_role(self, obj):
        return obj.role.name

    def get_pay(self, obj):
        return obj.get_pay

    def get_rate(self, obj):
        rate = obj.get_rate()
        if isinstance(rate, HourlyRate):
            minutes_worked = getattr(obj, 'minutes_worked', 0)
            return rate.rate * minutes_worked
        if rate and hasattr(rate, "rate"):
            return rate.rate
        return None


class ContributorRoleField(serializers.Field):
    """This is fucking stupid, but it's basically a field that returns the the
    names of people who have contributed to this content under a certain role."""

    def __init__(self, role, *args, **kwargs):
        super(ContributorRoleField, self).__init__(*args, **kwargs)
        self.role = role
        self.source = "*"

    def to_representation(self, obj):
        qs = Contribution.objects.filter(content=obj, role=self.role).select_related("contributor")
        return ",".join([contribution.contributor.get_full_name() for contribution in qs])


class ContentReportingSerializer(serializers.ModelSerializer):

    content_type = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    feature_type = serializers.SerializerMethodField()
    url = serializers.URLField(source="get_absolute_url")
    value = serializers.SerializerMethodField('get_content_value')
    authors = serializers.SerializerMethodField()
    video_id = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = (
            "id", "title", "url", "content_type", "feature_type", "published", "authors",
            "video_id", "value"
        )

    def get_content_value(self, obj):
        try:
            contributions = obj.contributions.distinct()
        except:
            contributions = obj.contributions.instances
        request = self.context.get("request")
        now = timezone.now()
        start_date = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=now.tzinfo
        )
        if "start" in request.QUERY_PARAMS:
            start_date = dateparse.parse_date(request.QUERY_PARAMS["start"])

        end_date = now
        if "end" in request.GET:
            end_date = dateparse.parse_date(request.QUERY_PARAMS["end"])

        if "contributors" in request.QUERY_PARAMS:
            contributors = request.QUERY_PARAMS.getlist("contributors")
            contributions = contributions.filter(contributor__username__in=contributors)

        # contributions = contributions.filter(
        #     force_payment=False
        # ) | contributions.filter(
        #     payment_date__range=(start_date, end_date)
        # )

        total_cost = 0
        for contribution in contributions:
            cost = contribution.get_pay
            if cost:
                total_cost += cost
        return total_cost

    def get_content_type(self, obj):
        return obj.__class__.__name__

    def get_feature_type(self, obj):
        return getattr(obj.feature_type, "name", None)

    def get_video_id(self, obj):
        if hasattr(obj, 'videohub_ref'):
            return getattr(obj.videohub_ref, 'id')
        elif hasattr(obj, 'video'):
            return getattr(obj.video, 'id')
        return None

    def get_published(self, obj):
        return timezone.localtime(obj.published)

    def get_authors(self, obj):
        return ",".join([author.get_full_name() for author in obj.authors.all()])



class ContributorReportSerializer(serializers.Serializer):

    deadline = serializers.DateTimeField()
    start = serializers.DateTimeField()
