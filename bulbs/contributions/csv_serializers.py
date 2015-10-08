from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Contribution


contributor_cls = get_user_model()


class ContributionCSVSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contribution

    def to_representation(self, obj):
        return {
            'first_name': obj.contributor.first_name,
            'last_name': obj.contributor.last_name,
            'title': obj.content.title,
            'feature_type': obj.content.feature_type,
            'publish_date': obj.content.published,
            'rate': obj.get_pay,
            'payroll_name': '{0} {1}'.format(obj.contributor.first_name, obj.contributor.last_name)
        }
