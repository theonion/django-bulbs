import json
import base64
import hmac
import sha
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import reverse


def upload_successful(request):
    return HttpResponse("Upload successfull!")


def aws_attrs(request):

    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    directory = getattr(settings, 'video_directory', '')
    callback_url = 'http://' + request.get_host() + reverse('bulbs.videos.views.upload_successful')

    policy_dict = {
        "expiration": expiration.isoformat(),
        "conditions": [
            {"bucket": settings.VIDEO_BUCKET},
            {"acl": "private"},
            {"success_action_redirect": callback_url},
            ["starts-with", "$key", directory],
            ["starts-with", "$Content-Type", ""],
            ["content-length-range", 0, 104857600],
        ]
    }

    policy_document = json.dumps(policy_dict)
    policy = base64.b64encode(policy_document)
    signature = base64.b64encode(hmac.new(settings.AWS_SECRET_ACCESS_KEY, policy, sha).digest())

    contents = {
        'AWSAccessKeyId': settings.AWS_ACCESS_KEY_ID,
        'acl': 'private',
        'success_action_redirect': callback_url,
        'policy': policy,
        'signature': signature,
        'Content-Type': '$Content-Type',
        'bucket': settings.VIDEO_BUCKET,
        'directory': directory
    }
    response_string = "var aws_attrs = %s;" % json.dumps(contents)
    return HttpResponse(response_string, content_type="application/javascript")
