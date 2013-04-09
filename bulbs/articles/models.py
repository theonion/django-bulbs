from django.db import models

from bulbs.base.models import ContentBody
from bulbs.images.models import Image


class Article(ContentBody):
    image = models.ForeignKey(Image, null=True, blank=True)
    body = models.TextField()
