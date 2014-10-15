from collections import OrderedDict

from django.utils import timezone

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
            ("feature_type", obj.content.feature_type),
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

