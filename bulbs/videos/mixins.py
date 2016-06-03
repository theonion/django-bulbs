from django.db import models


class VideoMixin(models.Model):

    """Provides an OnionStudios (videohub) reference ID, standardized across all properties."""

    videohub_ref = models.ForeignKey("videohub_client.VideohubVideo", null=True, blank=True)

    class Meta:
        abstract = True
