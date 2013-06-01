from django.db import models
from bulbs.content.models import Contentish, Tagish


class TestContentObj(Contentish):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)

    def get_absolute_url(self):
        return "/testobject/%s" % self.pk


class TestContentObjTwo(Contentish):

    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)
    field3 = models.IntegerField()

    def get_feature_type(self):
        return "Overridden feature type"

    def get_absolute_url(self):
        return "/testobject2/%s" % self.pk


class Section(Tagish):

    description = models.TextField()
