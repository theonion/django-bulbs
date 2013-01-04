import requests
import json
import urlparse

from django.db import models
from django.conf import settings

from bulbs.images.models import Image


class Video(models.Model):
    title = models.CharField(max_length=255)
    poster = models.ForeignKey(Image, null=True, blank=True)
    original = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)

        if self.original and not self.sources.exists():
            path = urlparse.urlparse(self.original).path
            output_format_params = {
                'bucket': settings.VIDEO_BUCKET,
                'directory': settings.VIDEO_DIRECTORY,
                'pk': self.pk,
                'size': 'high'
            }
            payload = {
                'input': 's3:/%s' % path,
                'outputs': [
                    {
                        "format": "mp4",
                        "public": True,
                        "url": "s3://%(bucket)s/%(directory)s/%(pk)s/%(size)s.mp4" % output_format_params
                    },
                    {
                        "format": "webm",
                        "public": True,
                        "url": "s3://%(bucket)s/%(directory)s/%(pk)s/%(size)s.webm" % output_format_params
                    }
                ]
            }
            requests.post('https://app.zencoder.com/api/v2/jobs', data=json.dumps(payload), headers={'Zencoder-Api-Key': settings.ZENCODER_API_KEY})


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
