from django.db import models
from bulbs.base.models import ContentMixin


class TestContentObj(models.Model, ContentMixin):
    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)

    @staticmethod
    def get_content_url(content_object):
        return "/testobject/%s" % content_object.pk
