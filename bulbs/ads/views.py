import json
import sys

from django.core.urlresolvers import resolve, Resolver404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.test.client import RequestFactory

from .models import TargetingOverride


if sys.version_info.major == 3:
    import urllib.parse as urlparse
else:
    from urlparse import urlparse


@csrf_exempt
def targeting(request):
    if not (request.user and request.user.has_perm("ads.change_targetingoverride")):
        return HttpResponseForbidden(
            '{"detail": "You do not have permission to perform this action."}'
        )

    url = request.GET.get("url")
    if url is None:
        return HttpResponseNotFound()

    if url.startswith("http://") or url.startswith("https://"):
        parsed = urlparse(url)
        url = parsed.path

    try:
        view, args, kwargs = resolve(url)
    except Resolver404:
        return HttpResponseNotFound()

    req = RequestFactory().get(url)
    kwargs['request'] = req
    response = view(*args, **kwargs)
    if response.status_code != 200:
        return HttpResponseNotFound()

    targeting = response.context_data.get('targeting', {})

    if request.method == "POST":
        override_data = json.loads(request.body)
        for key, value in targeting.items():
            if value == override_data.get(key):
                del override_data[key]
        override, created = TargetingOverride.objects.get_or_create(url=url)
        override.targeting = override_data
        override.save()
        targeting.update(override_data)
    else:
        try:
            override = TargetingOverride.objects.get(url=url)
            targeting.update(override.targeting)
        except TargetingOverride.DoesNotExist:
            pass
    return HttpResponse(json.dumps(targeting), content_type="application/json")
