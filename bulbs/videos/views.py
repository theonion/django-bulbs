from django.apps import apps
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic.base import View
from django.views.decorators.cache import cache_control

################################################################################
# FIXME: Tuesday, August 12 (2016) Collin Miller:
# we are temporarily overriding the
# video redirect url `/v/3838` on theonion.com to work around some of our content
# items that reference the same videohub id.
# We are overriding the logic to prefer redirecting to the url for some
# FeatureTypes over others. Once editorial has pruned down the duplicates we
# will add a unique constraint on the videohub_ref_id and we can go back to the
# default redirect logic.
#
# The method temporary_workaround_to_choose_from_duplicate_videos will not be
# needed once this unique constraint is setup.
################################################################################


class VideoRedirectView(View):
    def get(self, request, videohub_ref_id):
        videos = self.get_videos_for_redirect(videohub_ref_id)
        video = self.temporary_workaround_to_choose_from_duplicate_videos(videos)

        if video is None:
            raise Http404("No video found with the provided videohub_ref id.")

        return HttpResponseRedirect(video.get_absolute_url())

    def temporary_workaround_to_choose_from_duplicate_videos(self, videos):
        if videos:
            return videos[0]

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
