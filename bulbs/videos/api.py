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
    sources = JSONField()

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
            s3_path = os.path.join(settings.VIDEO_ENCODING['bucket'], settings.VIDEO_ENCODING['directory'], video.pk)
        except KeyError:
            raise ImproperlyConfigured("Video encoding settings aren't defined.")

        base_url = "s3://%d" % s3_path

        payload = {
            'input': '%s/original' % base_url,
            'outputs': [],
            'notifications': [{
                "url": "http://videoads.theonion.com%s" % reverse('videoads.videos.views.notification'),
                "format": "json"
            }]
        }

        output_update = {
            'base_url': base_url,
            'public': True
        }
        for output_template in settings.VIDEO_ENCODING.get('outputs', []):
            output = copy.copy(output_template)
            output.update(output_update)
            payload['outputs'].append(output)

        auth_headers = {'Zencoder-Api-Key': settings.VIDEO_ENCODING.get('zencoder_api_key')}
        response = requests.post("https://app.zencoder.com/api/v2/jobs", data=json.dumps(payload), headers=auth_headers)
        from raven import Client
        client = Client('http://fad3598fbbfc45a3857c31dda948a975:cbfa1ddba9ac43bfa83b5f1daf218a12@sentry.onion.com/7')
        client.captureMessage('Zencoder response: %s' % response.content)
        if response.status_code == 201:
            video.job_id = response.json().get('id')
            video.status = Video.IN_PROGRESS
            video.data = response.json()
            video.save()

        return Response(response.json(), status_code=response.status_code)

router = routers.SimpleRouter()
router.register('video', VideoViewSet)