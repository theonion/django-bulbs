from rest_framework import serializers

from .models import SpecialCoverage


class SpecialCoverageSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = SpecialCoverage
