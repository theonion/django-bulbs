from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils import timezone

from bulbs.content.models import Content, FeatureType
from bulbs.content.serializers import FeatureTypeField, UserSerializer

from rest_framework import serializers
from rest_framework.utils import model_meta

from .models import (Contribution, ContributorRole, HourlyRate, FlatRate, ManualRate, FeatureTypeRate, FeatureTypeOverride, LineItem, Override, Rate, RATE_PAYMENT_TYPES)


class PaymentTypeField(serializers.Field):
    """
    payment type objects serialized to/from label/identifer
    """
    def to_representation(self, obj):
        return dict(RATE_PAYMENT_TYPES)[obj]

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
        Contributor = get_user_model()
        if isinstance(data, int):
            return Contributor.objects.get(id=data)
        elif isinstance(data, dict):
            id = data.get("id", None)
            if id is not None:
                return Contributor.objects.get(id=id)
        return None


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
            rate = ManualRate(**data)
        elif 'feature_type' in data:
            rate = FeatureTypeRate(**data)
        else:
            rate = Rate(**data)
        rate.save()
        return rate


class ContributorRoleSerializer(serializers.ModelSerializer):

    payment_type = PaymentTypeField()

    class Meta:
        model = ContributorRole

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
                    FeatureTypeRate.objects.create(
                        role=instance,
                        feature_type=ft,
                        **feature_type
                    )

        return instance


class ContributorRoleField(serializers.Field):

    def to_representation(self, obj):
        return ContributorRoleSerializer(obj).data

    def to_internal_value(self, data):
        if isinstance(data, int):
            return ContributorRole.objects.get(id=data)
        elif isinstance(data, dict):
            id = data.get("id", None)
            return ContributorRole.objects.get(id=id)
        return None


class FeatureTypeOverrideSerializer(serializers.ModelSerializer):

    contributor = ContributorField()
    role = ContributorRoleField()
    feature_type = FeatureTypeField(queryset=FeatureType.objects.all())

    class Meta:
        model = FeatureTypeOverride


class OverrideSerializer(serializers.ModelSerializer):

    contributor = ContributorField()
    role = ContributorRoleField()

    class Meta:
        model = Override

    def create(self, validated_data):
        if "feature_type" in validated_data:
            return FeatureTypeOverrideSerializer().create(validated_data)
        else:
            return super(OverrideSerializer, self).create(validated_data)

    def to_internal_value(self, data):
        if "feature_type" in data:
            return FeatureTypeOverrideSerializer().to_internal_value(data)
        else:
            return super(OverrideSerializer, self).to_internal_value(data)

    def to_representation(self, obj):
        if isinstance(obj, FeatureTypeOverride):
            return FeatureTypeOverrideSerializer(obj).to_representation(obj)
        else:
            return super(OverrideSerializer, self).to_representation(obj)


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
        data = super(ContributionSerializer, self).to_internal_value(data)
        if rate_data:
            data['rate'] = rate_data
        return data

    def create(self, validated_data):
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        rate_data = validated_data.pop('rate', None)
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)
        contribution = ModelClass.objects.create(**validated_data)
        if rate_data:
            rate_data['contribution'] = contribution
            RateField().to_internal_value(rate_data)
        return contribution


class ContributionReportingSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Contribution
        fields = ("id", "content", "user", "role", "notes")

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
    authors = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ("id", "title", "url", "content_type", "feature_type", "published", "authors")

    def get_fields(self):

        fields = super(ContentReportingSerializer, self).get_fields()

        self._roles = {}
        for role in ContributorRole.objects.all():
            fields[role.name.lower()] = ContributorRoleField(role)

        return fields

    def get_contributors(self, obj, rolename):
        pass

    def get_content_type(self, obj):
        return obj.__class__.__name__

    def get_feature_type(self, obj):
        return getattr(obj.feature_type, "name", None)

    def get_published(self, obj):
        return timezone.localtime(obj.published)

    def get_authors(self, obj):
        return ",".join([author.get_full_name() for author in obj.authors.all()])
