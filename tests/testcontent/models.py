from django.db import models

from bulbs.content.models import Content

class TestContentObj(Content):
    """Fake content here"""
    foo = models.CharField(max_length=255)

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class TestContentObjTwo(Content):
    """Come and get your fake content"""
    foo = models.CharField(max_length=255)
    bar = models.IntegerField()

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk
