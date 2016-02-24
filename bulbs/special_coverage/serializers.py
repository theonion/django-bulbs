from rest_framework import serializers

from bulbs.utils.serializers import JSONField
from bulbs.content.mixins import ImageSerializerMixin

from .models import SpecialCoverage


class SpecialCoverageSerializer(ImageSerializerMixin, serializers.ModelSerializer):

    query = JSONField(required=False, default={})
    videos = JSONField(required=False, default=[])
    config = JSONField(required=False, default={})

    class Meta:
        model = SpecialCoverage
