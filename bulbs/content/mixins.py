from django.db import models

from djbetty.fields import ImageField
from djbetty.serializers import ImageFieldSerializer

from rest_framework import serializers


class BodyMixin(models.Model):
    """Provides a "body" field which contains HTML but is not included in the ES index body."""
    body = models.TextField(blank=True, default="")

    class Meta:
        abstract = True

class DetailImageMixin(models.Model):
    """Provides an "image" field, with caption and alt."""
    _image_caption = models.CharField(null=True, blank=True, editable=False, max_length=255)
    _image_alt = models.CharField(null=True, blank=True, editable=False, max_length=255)
    image = ImageField(null=True, blank=True, alt_field="_image_alt", caption_field="_image_caption")

    class Meta:
        abstract = True

class ImageSerializerMixin(serializers.Serializer):

    image = ImageFieldSerializer(required=False, allow_null=True)

    class Meta:
        abstract = True
