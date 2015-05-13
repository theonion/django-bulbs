from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer
from bulbs.utils.serializers import JSONField

from .models import Section


class SectionSerializer(serializers.ModelSerializer):

    query = JSONField(required=False, default={})
    section_logo = ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        model = Section
