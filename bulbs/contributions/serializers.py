from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils import timezone

from bulbs.content.models import Content, FeatureType
from bulbs.content.serializers import FeatureTypeField, UserSerializer
from rest_framework import serializers
from rest_framework.utils import model_meta
import six

from .models import (
    Contribution, ContributorRole, ContributionOverride, HourlyRate, FlatRate, ManualRate,
    FeatureTypeRate, FeatureTypeOverride, LineItem, Override, FeatureTypeOverrideProfile, Rate,
    RATE_PAYMENT_TYPES
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
        if isinstance(data, int):
            return contributor_cls.objects.get(id=data)
        elif isinstance(data, dict):
            id = data.get("id", None)
            if id is not None:
                return contributor_cls.objects.get(id=id)
        return None


class FreelanceProfileSerializer(serializers.Serializer):

    contributor = ContributorField()
    payment_date = serializers.DateTimeField()
    pay = serializers.SerializerMethodField()
    contributions_count = serializers.SerializerMethodField("get_contribution_count")

    def get_pay(self, obj):
        return obj.get_pay()

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
            data["name"] = 3
            rate = ManualRate(**data)
        elif 'feature_type' in data:
            rate = FeatureTypeRate(**data)
        else:
            rate = Rate(**data)
        rate.save()
        return rate


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

    def to_representation(self, obj):
        data = super(ContributorRoleSerializer, self).to_representation(obj)
        rates = {}

        flat_rate = FlatRate.objects.filter(role=obj).first()
        if flat_rate:
            rates["flat_rate"] = {
                "rate": flat_rate.rate,
                "updated_on": flat_rate.updated_on.isoformat()
            }

        hourly = HourlyRate.objects.filter(role=obj).first()
        if hourly:
            rates["hourly"] = {
                "rate": hourly.rate,
                "updated_on": hourly.updated_on.isoformat()
            }

        feature_types = []

        role_qs = FeatureTypeRate.objects.filter(role=obj)
        slugs = role_qs.order_by(
            "feature_type__slug"
        ).values_list(
            "feature_type__slug", flat=True
        ).distinct()

        for slug in slugs:
            ft = role_qs.filter(feature_type__slug=slug).first()
            feature_types.append({
                "feature_type": ft.feature_type.name,
                "rate": ft.rate,
                "updated_on": ft.updated_on.isoformat()
            })
        if feature_types:
            rates["feature_type"] = feature_types

        data["rates"] = rates
        return data

    def to_internal_value(self, data):
        rates = data.pop("rates", {})
        data = super(ContributorRoleSerializer, self).to_internal_value(data)
        data["rates"] = rates
        return data

    def save(self):
        rates = self.validated_data.pop("rates", None)
        instance = super(ContributorRoleSerializer, self).save()

        flat_rate = rates.get("flat_rate", None)
        if flat_rate:
            FlatRate.objects.create(role=instance, **flat_rate)

        hourly = rates.get("hourly", None)
        if hourly:
            HourlyRate.objects.create(role=instance, **hourly)

        feature_types = rates.get("feature_type")
        if feature_types:
            for feature_type in feature_types:
                name = feature_type.pop("feature_type", None)
                if name:
                    slug = slugify(name)
                    ft, created = FeatureType.objects.get_or_create(
                        slug=slug,
                        defaults={"name": name}
                    )
                    rate = FeatureTypeRate.objects.filter(role=instance, feature_type=ft)
                    if not rate.exists():
                        rate = FeatureTypeRate.objects.create(
                            role=instance, feature_type=ft, rate=0
                        )
                    else:
                        rate = rate.first()

                    for key, value in feature_type.items():
                        setattr(rate, key, value)
                    rate.save()

        return instance


class RoleField(serializers.Field):

    def get_attribute(self, obj):
        return (obj.role, obj)

    def to_representation(self, obj):
        obj, contribution = obj
        data = ContributorRoleSerializer(obj).data
        if isinstance(contribution, Contribution):
            rate = data.get("rate")
            if not rate:
                rate = contribution.get_rate()
                if rate and hasattr(rate, "rate"):
                    data["rate"] = rate.rate
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


class OverrideSerializer(serializers.ModelSerializer):

    contributor = ContributorField()
    rate = serializers.IntegerField(required=False, allow_null=True)
    role = RoleField()

    class Meta:
        model = Override

    def get_feature_types(self, obj):
        return FeatureTypeOverrideProfile.objects.filter(
            role=obj.role,
            contributor=obj.contributor
        )

    def update_feature_type_overrides(self, profile, feature_types):
        for data in feature_types:
            ft_data = data.get('feature_type', None)
            if ft_data:
                feature_type = FeatureTypeField(read_only=True).to_internal_value(
                    ft_data
                )
                rate = int(data.get('rate', 0))
                ft_override = profile.feature_types.get_or_create(
                    feature_type=feature_type,
                )[0]
                if ft_override.rate != rate:
                    ft_override.rate = rate
                    ft_override.save()

    def feature_type_internal(self, validated_data, instance=None):
        feature_types = validated_data.pop("feature_types", [])
        if feature_types:
            role = validated_data.get('role', None)
            contributor = validated_data.get('contributor', None)
            if not instance or not isinstance(instance, FeatureTypeOverrideProfile):
                instance, created = FeatureTypeOverrideProfile.objects.get_or_create(
                    role=role,
                    contributor=contributor
                )
            self.update_feature_type_overrides(instance, feature_types)
            return instance
        return None

    def to_internal_value(self, data):
        feature_types = data.pop("feature_types", None)
        override = super(OverrideSerializer, self).to_internal_value(data)
        if feature_types:
            override['feature_types'] = feature_types
        return override

    def create(self, validated_data):
        feature_type = self.feature_type_internal(validated_data)
        if feature_type:
            return feature_type
        return super(OverrideSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        feature_type = self.feature_type_internal(validated_data, instance=instance)
        if feature_type:
            return feature_type
        return super(OverrideSerializer, self).update(validated_data)

    def to_representation(self, obj):
        if isinstance(obj, FeatureTypeOverride):
            data = FeatureTypeOverrideSerializer(obj).to_representation(obj)
        else:
            data = super(OverrideSerializer, self).to_representation(obj)

        feature_types = []

        feature_types_qs = self.get_feature_types(obj).first()
        if feature_types_qs:
            for feature_type in feature_types_qs.feature_types.all().order_by('-updated_on'):
                feature_types.append(
                    FeatureTypeOverrideSerializer(
                        feature_type
                    ).to_representation(
                        feature_type
                    )
                )
        data["feature_types"] = feature_types
        return data


class ContributionOverrideField(serializers.Field):

    def get_attribute(self, obj):
        return obj.get_override

    def to_representation(self, obj):
        return obj


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
        return {
            "id": obj.contributor.id,
            "username": obj.contributor.username,
            "full_name": obj.contributor.get_full_name(),
        }

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

    class Meta:
        model = Content
        fields = ("id", "title", "url", "content_type", "feature_type", "published", "authors", "value")

    def get_content_value(self, obj):
        contributions = obj.contributions.all()
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

    def get_published(self, obj):
        return timezone.localtime(obj.published)

    def get_authors(self, obj):
        return ",".join([author.get_full_name() for author in obj.authors.all()])
