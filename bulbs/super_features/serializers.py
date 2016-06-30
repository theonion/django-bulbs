from rest_framework import serializers

from .models import SuperFeature


class SuperFeatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperFeature
