from rest_framework import serializers

from .models import SpecialCoverage


class SpecialCoverageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecialCoverage
