from django.db import models

from bulbs.images.models import Image


class Video(models.Model):
    title = models.CharField(max_length=255)
    poster = models.ForeignKey(Image)
    original = models.URLField()


class VideoSource(models.Model):
    src = models.URLField()
    type = models.CharField(max_length=100)
