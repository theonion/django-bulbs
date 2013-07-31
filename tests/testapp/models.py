from django.db import models
from bulbs.content.models import Content, ReadonlyRelatedManager, Tag


class TestContentObj(Content):

    foo = models.CharField(max_length=255)

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class TestContentObjTwo(Content):

    foo = models.CharField(max_length=255)
    bar = models.IntegerField()

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class ROBud(object):
    foo = ReadonlyRelatedManager()

