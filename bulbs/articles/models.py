from django.db import models

from bulbs.base.models import ContentBase
from bulbs.images.models import Image


class Article(ContentBase):
    body = models.TextField()
