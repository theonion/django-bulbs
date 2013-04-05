from django.db import models
from bulbs.base.models import ContentBase


class TestContentObj(ContentBase):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)

    def get_absolute_url(self):
        return "/testobject/%s" % self.pk


class TestContentObjTwo(ContentBase):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)
    field3 = models.IntegerField()

    def get_absolute_url(self):
        return "/testobject2/%s" % self.pk
