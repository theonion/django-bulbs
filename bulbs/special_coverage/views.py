from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.content.views import BaseContentDetailView


class SpecialCoverageView(BaseContentDetailView):
    redirect_correct_path = False

    def show_published_only(self):
        return bool("full_preview" not in self.request.GET)

    def get_template_names(self):
        template_names = ["special_coverage/default.html"]

        extended = getattr(settings, 'SPECIAL_COVERAGE_LANDING_TEMPLATE', None)
        if extended:
            template_names.append(extended)

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

        return context


special_coverage = SpecialCoverageView.as_view()
