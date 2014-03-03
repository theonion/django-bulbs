import json
import base64
import hmac
import hashlib
import datetime

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control


from .models import Video


@cache_control(no_cache=True)
@csrf_exempt
def notification(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["GET"])

    # Grab the encoding details from message
    details = json.loads(request.body)

    sources = []
    """We need to munge the encoding details into an easily rendered list of sources:
    {
        "url"         : "http://example.com/some_video.mp4",
        "content_type": "video/mp4",
        "height"      : 320,
        "width"       : 640,
        "bitrate"     : 120
    }

    "url" and "content_type" are the only required properties, with "width", "height" and "bitrate"
    being only available for some items.
    """
    for output in details.get('outputs', []):
        for filename in settings.VIDEO_ENCODING.get('sources', {}).keys():
            if output.get('url').endswith(filename):
                source = {
                    'url': output['url'],
                    'content_type': settings.VIDEO_ENCODING.get('sources', {}).get(filename)
                }
                if output.get('height'):
                    source['height'] = output['height']

                if output.get('width'):
                    source['width'] = output['width']

                if output.get('video_bitrate_in_kbps'):
                    source['bitrate'] = output['video_bitrate_in_kbps']

                sources.append(source)
                break

    job_id = details['job']['id']
    videos = Video.objects.filter(job_id=job_id)
    if videos.count() == 1:
        video = videos[0]
        video.data = details
        video.sources = sources

        if details['job']['state'] == 'finished':
            video.status = Video.COMPLETE
        if details['job']['state'] in ['cancelled', 'failed']:
            video.status = Video.FAILED
        video.save()
    return HttpResponse(status=204)


@cache_control(no_cache=True)
@staff_member_required
def video_attrs(request):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    directory = settings.VIDEO_ENCODING.get('directory')
    # callback_url = 'http://' + request.get_host() + reverse('videoads.videos.views.upload_successful')

    policy_dict = {
        "expiration": expiration.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        "conditions": [
            {"bucket": settings.VIDEO_ENCODING.get('bucket')},
            {"acl": "private"},
            {"success_action_status": '201'},
            ["starts-with", "$key", directory],
            ["content-length-range", 0, 1073741824],
        ]
    }

    policy_document = json.dumps(policy_dict)
    policy = base64.b64encode(policy_document)
    signature = base64.b64encode(
        hmac.new(settings.AWS_SECRET_ACCESS_KEY, policy, hashlib.sha1).digest())

    contents = {
        'AWSAccessKeyId': settings.AWS_ACCESS_KEY_ID,
        'acl': 'private',
        'success_action_status': '201',
        'policy': policy,
        'signature': signature,
        'Content-Type': '$Content-Type',
        'bucket': settings.VIDEO_ENCODING.get('bucket'),
        'directory': directory,
        'zencoderApiKey': settings.VIDEO_ENCODING.get('zencoder_api_key')
    }
    response_string = "var videoAttrs = %s;" % json.dumps(contents)
    return HttpResponse(response_string, content_type="application/javascript")
