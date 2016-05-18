from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from .models import Contribution, LineItem


contributor_cls = get_user_model()


class ContributionCSVSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contribution

    def to_representation(self, obj):
        full_name = obj.contributor.get_full_name()
        data = {
            'id': obj.content.id,
            'first_name': obj.contributor.first_name,
            'last_name': obj.contributor.last_name,
            'title': obj.content.title,
            'feature_type': obj.content.feature_type,
            'publish_date': timezone.localtime(obj.content.published),
            'rate': obj.get_pay,
            'payroll_name': full_name
        }
        profile = getattr(obj.contributor, 'freelanceprofile', None)
        if profile:
            payroll_name = getattr(profile, 'payroll_name', None)
            if payroll_name:
                data['payroll_name'] = payroll_name
        return data


class LineItemCSVSerializer(serializers.ModelSerializer):

    class Meta:
        model = LineItem

    def to_representation(self, obj):
        data = {
            "amount": obj.amount,
            "note": obj.note,
            "payment_date": timezone.localtime(obj.payment_date),
            "payroll_name": obj.contributor.get_full_name()
        }
        profile = getattr(obj.contributor, "freelanceprofile", None)
        if profile:
            payroll_name = getattr(profile, "payroll_name", None)
            if payroll_name:
                data["payroll_name"] = payroll_name
        return data
