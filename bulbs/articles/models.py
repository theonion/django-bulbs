from django.db import models

from bulbs.base.models import Contentish
from bulbs.images.models import Image


class Article(Contentish):
    body = models.TextField()
