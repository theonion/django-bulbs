from django.db import models

from .models import VideohubVideo


class VideoMixin(models.Model):

    """Provides an OnionStudios (videohub) reference ID, standardized across all properties."""

    videohub_ref = models.ForeignKey(VideohubVideo, null=True, blank=True)

    class Meta:
        abstract = True
