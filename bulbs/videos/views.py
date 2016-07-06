from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control


@cache_control(max_age=3600)
def video_redirect(request, videohub_ref_id):
    video_model_name = getattr(settings, "VIDEO_MODEL", "")
    video_model = apps.get_model(video_model_name)
    try:
        video = get_object_or_404(video_model, videohub_ref__id=int(videohub_ref_id))
    except FieldError:
        raise Http404("No video found with the provided videohub_ref id.")
    return HttpResponseRedirect(video.get_absolute_url())
