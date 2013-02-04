import requests
import json

from django.db import models
from django.conf import settings

from bulbs.images.models import Image

DEFAULT_VIDEO_OUTPUT = {
    "public": True,
    "width": 640,
    "height": 320
}


class Video(models.Model):
    title = models.CharField(max_length=255)
    poster = models.ForeignKey(Image, null=True, blank=True)
    original = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)

        if self.original and not self.sources.exists() and hasattr(settings, 'ZENCODER_OUTPUTS'):

            output_directory = getattr(settings, 'VIDEO_OUTPUT_DIRECTORY', 'videos/output')
            outputs = []
            for output in settings.ZENCODER_OUTPUTS:
                output.update(DEFAULT_VIDEO_OUTPUT)
                output['url'] = "s3://%s/%s/%s/%s.%s" % (settings.VIDEO_BUCKET, output_directory, self.pk, output['width'], output['format'])
                outputs.append(output)

            payload = {
                'input': self.original,
                'outputs': outputs
            }

            auth_headers = {'Zencoder-Api-Key': settings.ZENCODER_API_KEY}
            response = requests.post('https://app.zencoder.com/api/v2/jobs', data=json.dumps(payload), headers=auth_headers)

            for output in response.json()['outputs']:
                src = output['url']
                # TODO: Maybe use os.path.splittext ?
                extension = src.split(".")[-1]

                VideoSource.objects.create(video=self, type="video/%s" % extension, src=src, zencoder_output_id=output['id'])


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

    # TODO: check progress output https://app.zencoder.com/docs/api/outputs/progress
    zencoder_output_id = models.CharField(max_length=100, null=True, blank=True)
