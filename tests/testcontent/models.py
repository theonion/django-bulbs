from django.db import models

from bulbs.content.models import Content, Tag
from djbetty.fields import ImageField


class TestContentObj(Content):
    """Fake content here"""
    foo = models.CharField(max_length=255)

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk

    @classmethod
    def get_serializer_class(cls):
        from .serializers import TestContentObjSerializer
        return TestContentObjSerializer


class TestContentObjTwo(Content):
    """Come and get your fake content"""
    foo = models.CharField(max_length=255)
    bar = models.IntegerField()

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class TestCategory(Tag):

    baz = models.CharField(max_length=255)


class TestContentDetailImage(TestContentObj):

    detail_caption = models.CharField(null=True, blank=True, max_length=255)
    detail_alt = models.CharField(null=True, blank=True, max_length=255)

    detail_image = ImageField(null=True, blank=True, caption_field="detail_caption", alt_field="detail_alt")

    @classmethod
    def get_serializer_class(cls):
        from .serializers import TestContentDetailImageSerializer
        return TestContentDetailImageSerializer

