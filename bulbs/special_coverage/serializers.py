from rest_framework import serializers

from bulbs.utils.serializers import JSONField

from .models import SpecialCoverage


class SpecialCoverageSerializer(serializers.ModelSerializer):

    query = JSONField(required=False, default={})
    videos = JSONField(required=False, default=[])
    config = JSONField(required=False, default={})

    class Meta:
        model = SpecialCoverage
