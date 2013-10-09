from django.db import models

from json_field import JSONField
from bulbs.images.fields import RemoteImageField


DEFAULT_VIDEO_OUTPUT = {
    "public": True,
    "width": 640,
    "height": 320
}


class Video(models.Model):
    """This is a very lightweight model that basically wraps an externally available set of sources
    for a given video."""

    NOT_STARTED = 0
    COMPLETE = 1
    IN_PROGRESS = 2
    FAILED = 3
    STATUSES = (
        (NOT_STARTED, 'Not started'),
        (COMPLETE, 'Complete'),
        (IN_PROGRESS, 'In Progress'),
        (FAILED, 'Failed')
    )

    name = models.CharField(max_length=255)
    data = JSONField(null=True, blank=True, help_text="This is JSON taht is returned from an encoding job")
    sources = JSONField(null=True, blank=True, default=[], help_text="This is a JSON array of sources.")
    poster = RemoteImageField(null=True, blank=True)

    def __unicode__(self):
        return self.name
