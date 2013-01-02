from django.db import models
from bulbs.base.models import ContentMixin


class TestContentObj(models.Model, ContentMixin):
    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)
