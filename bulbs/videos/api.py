import os
import copy
import requests
import json

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.conf import settings

from rest_framework import serializers
from rest_framework import fields
from rest_framework import viewsets
from rest_framework import decorators
from rest_framework import routers
from rest_framework.response import Response

from .models import Video
from bulbs.content.models import LogEntry


class JSONField(serializers.WritableField):
    def to_native(self, obj):
        if obj is None:
            return self.default
        return obj

    def from_native(self, data):
        if data is None:
            return self.default
        return data


class VideoSerializer(serializers.ModelSerializer):

    status = fields.Field(source='get_status_display')
    sources = JSONField(required=False)

    class Meta:
        model = Video
        exclude = ("data",)
        read_only_fields = ("id", "job_id")


class VideoViewSet(viewsets.ModelViewSet):

    model = Video
    serializer_class = VideoSerializer

    @decorators.action()
    def encode(self, request, pk=None):
        video = self.get_object()
        if 'name' in request.POST:
            video.name = request.POST.get('name')

        try:
            s3_path = os.path.join(
                settings.VIDEO_ENCODING['bucket'],
                settings.VIDEO_ENCODING['directory'],
                str(video.pk))
        except KeyError:
            raise ImproperlyConfigured("Video encoding settings aren't defined.")

        base_url = "s3://%s" % s3_path
        default_notification_url = request.build_absolute_uri(
            reverse('bulbs.videos.views.notification'))

        payload = {
            'input': '%s/original' % base_url,
            'outputs': [],
            'notifications': [{
                "url": settings.VIDEO_ENCODING.get("notification_url", default_notification_url),
                "format": "json"
            }]
        }

        output_update = {
            'base_url': base_url,
            'public': True
        }
        for output_template in settings.VIDEO_ENCODING.get('outputs', []):
            output = copy.copy(output_template)
            if "thumbnails" in output_template:
                output["thumbnails"].update(output_update)
            else:
                output.update(output_update)
            payload['outputs'].append(output)

        auth_headers = {'Zencoder-Api-Key': settings.VIDEO_ENCODING.get('zencoder_api_key')}
        response = requests.post(
            "https://app.zencoder.com/api/v2/jobs",
            data=json.dumps(payload), headers=auth_headers)
        if response.status_code == 201:
            video.job_id = response.json().get('id')
            video.status = Video.IN_PROGRESS
            video.data = response.json()
            video.save()
            if request.user.is_authenticated():
                LogEntry.objects.log(request.user, video, "Encoded")
            else:
                LogEntry.objects.log(None, video, "Encoded")

        return Response(response.json(), status=response.status_code)

    def post_save(self, obj, created=False):
        message = "Created" if created else "Saved"
        if self.request.user.is_authenticated():
            LogEntry.objects.log(self.request.user, obj, message)
        else:
            LogEntry.objects.log(None, obj, message)
        return super(VideoViewSet, self).post_save(obj, created=created)

router = routers.SimpleRouter()
router.register('video', VideoViewSet)
