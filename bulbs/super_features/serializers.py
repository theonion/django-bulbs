from rest_framework import serializers

from .models import Page


class SuperFeatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page
