from rest_framework import serializers

from .models import SpecialCoverage


class SpecialCoverageSerializer(serializers.ModelSerializer):

# TODO : make videos a list of ids or something???

    class Meta:
        model = SpecialCoverage
