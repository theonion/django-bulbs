from collections import OrderedDict

from django.utils import timezone

from bulbs.content.models import Content
from bulbs.content.serializers import UserSerializer

from rest_framework import serializers

from .models import Contribution, ContributorRole


class ContributorRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContributorRole


class ContributionSerializer(serializers.ModelSerializer):

    contributor = UserSerializer()

    class Meta:
        model = Contribution


class ContributionReportingSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField("get_user")
    content = serializers.SerializerMethodField("get_content")
    role = serializers.SerializerMethodField("get_role")

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

    def to_native(self, obj):
        qs = Contribution.objects.filter(content=obj, role=self.role).select_related("user")
        return ",".join([contribution.contributor.get_full_name() for contribution in qs])


class ContentReportingSerializer(serializers.ModelSerializer):

    content_type = serializers.SerializerMethodField("get_content_type")
    published = serializers.SerializerMethodField("get_published")
    url = serializers.URLField(source="get_absolute_url")

    class Meta:
        model = Content
        fields = ("id", "title", "url", "content_type", "feature_type", "published")

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

    def get_published(self, obj):
        return timezone.localtime(obj.published)
