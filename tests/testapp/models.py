from django.db import models
from bulbs.polycontent.models import Content


class TestContentObj(Content):

    field1 = models.CharField(max_length=255)

    def get_absolute_url(self):
        return "/detail/%s/" % self.pk


class TestContentObjTwo(Content):

    field1 = models.CharField(max_length=255)
    field2 = models.IntegerField()

    def get_feature_type(self):
        return "Overridden feature type"

    def get_absolute_url(self):
        return "/detail/%s/" % self.pk

