from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_control

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.content.views import BaseContentDetailView


class SpecialCoverageView(BaseContentDetailView):
    redirect_correct_path = False

    def get_template_names(self):
        template_names = ["special_coverage/landing.html"]
        return template_names

    def get_object(self, *args, **kwargs):
        self.special_coverage = get_object_or_404(SpecialCoverage, slug=self.kwargs.get("slug"))

        if not self.special_coverage.is_active:
            raise Http404("Special Coverage does not exist.")

        qs = self.special_coverage.get_content(published=self.show_published_only()).full()
        if qs.count() == 0:
            raise Http404("No Content available in content list")

        return qs[0]

    def get_context_data(self, *args, **kwargs):
        context = super(SpecialCoverageView, self).get_context_data()
        context["content_list"] = self.special_coverage.get_content()
        context["special_coverage"] = self.special_coverage
        context["targeting"] = {}
        try:
            context["current_video"] = self.special_coverage.videos[0]
        except IndexError:
            context["current_video"] = None

        if self.special_coverage:
            context["targeting"]["dfp_specialcoverage"] = self.special_coverage.slug
            if self.special_coverage.tunic_campaign_id:
                context["targeting"]["dfp_campaign_id"] = self.special_coverage.tunic_campaign_id
        return context


class SpecialCoverageVideoView(SpecialCoverageView):
    def get_context_data(self, *args, **kwargs):
        context = super(SpecialCoverageVideoView, self).get_context_data()

        video_id = int(self.kwargs.get('video_id'))
        if video_id not in self.special_coverage.videos:
            raise Http404('Video with id={} not in SpecialCoverage'.format(video_id))

        context['current_video'] = video_id

        return context


special_coverage = cache_control(max_age=600)(SpecialCoverageView.as_view())
special_coverage_video = cache_control(max_age=600)(SpecialCoverageVideoView.as_view())
