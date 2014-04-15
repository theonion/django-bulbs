from django.db import models

from json_field import JSONField


DEFAULT_VIDEO_OUTPUT = {
    "public": True,
    "width": 640,
    "height": 320
}


VIDEO_PREFERENCES = {
    "video/mp4" : 0.75,
    "video/webm": 1.25
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
    data = JSONField(null=True, blank=True, help_text="This is JSON that is returned from an encoding job")
    sources = JSONField(null=True, blank=True, default=[], help_text="This is a JSON array of sources.")
    poster_url = models.URLField(null=True, blank=True)
    status = models.IntegerField(choices=STATUSES, default=NOT_STARTED)
    job_id = models.IntegerField(null=True, blank=True, help_text="The zencoder job ID")

    def __unicode__(self):
        return self.name

    def ordered_sources(self):
        return sorted(
            self.sources,
            key=lambda source: VIDEO_PREFERENCES.get(
                source['content_type'], 1
            ) * source.get('width', 1))
