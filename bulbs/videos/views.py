from django.apps import apps
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic.base import View
from django.views.decorators.cache import cache_control


class VideoRedirectView(View):
    def get(self, request, videohub_ref_id):
        videos = self.get_videos_for_redirect(videohub_ref_id)
        video = self.choose_video_for_redirect(videos)

        if video is None:
            raise Http404("No video found with the provided videohub_ref id.")

        return HttpResponseRedirect(video.get_absolute_url())

    def choose_video_for_redirect(self, videos):
        if len(videos) is 0:
            video = None
        elif len(videos) is 1:
            video = videos[0]
        else:
            video = videos

        return video

    def get_videos_for_redirect(self, videohub_ref_id):
        video_model_name = getattr(settings, "VIDEO_MODEL", "")
        video_model = apps.get_model(video_model_name)
        videos = video_model.objects.filter(
            videohub_ref__id=int(videohub_ref_id),
            published__lte=timezone.now(),
        ).order_by(
            '-published'
        ).all()

        return videos

video_redirect = cache_control(max_age=3600)(VideoRedirectView.as_view())
