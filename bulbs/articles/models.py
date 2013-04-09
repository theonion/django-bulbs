from django.db import models

from bulbs.base.models import ContentBase
from bulbs.images.models import Image


class Article(ContentBase):
    image = models.ForeignKey(Image, null=True, blank=True)
    body = models.TextField()
