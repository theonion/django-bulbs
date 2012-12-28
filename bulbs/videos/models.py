from django.db import models

from bulbs.base.models import ContentMixin
from bulbs.images.models import Image


class Video(models.Model, ContentMixin):
    title = models.CharField(max_length=255)
    poster = models.ForeignKey(Image, null=True, blank=True)
    original = models.URLField(null=True, blank=True)


class VideoSource(models.Model):

    TYPE_CHOICES = (
        ('video/mp4', 'video/mp4'),
        ('video/webm', 'video/webm'),
        ('video/vimeo', 'video/vimeo'),
        ('video/youtube', 'video/youtube'),
    )

    video = models.ForeignKey(Video, related_name='sources')
    src = models.URLField()
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
