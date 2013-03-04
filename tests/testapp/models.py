from django.db import models
from bulbs.base.models import ContentDelegateBase


class TestContentObj(ContentDelegateBase):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)

    @staticmethod
    def get_content_url(content_object):
        return "/testobject/%s" % content_object.pk


class TestContentObjTwo(ContentDelegateBase):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)
    field3 = models.IntegerField()

    @staticmethod
    def get_content_url(content_object):
        return "/testobject2/%s" % content_object.pk
