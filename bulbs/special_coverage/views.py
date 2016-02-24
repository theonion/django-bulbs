from django.views.generic import DetailView
from django.http import Http404
from django.shortcuts import get_object_or_404


from bulbs.special_coverage.models import SpecialCoverage


class SpecialCoverageView(DetailView):

    def show_published_only(self):
        return bool("full_preview" not in self.request.GET)

    def get_object(self, *args, **kwargs):
        self.special_coverage = get_object_or_404(SpecialCoverage, slug=self.kwargs.get("slug"))
        if not self.special_coverage.is_active:
            raise Http404("Special Coverage does not exist.")
        return self.special_coverage.get_content(published=self.show_published_only()).full()[0]

    def get_context_data(self, *args, **kwargs):
        context = super(SpecialCoverageView, self).get_context_data()
        context["content_list"] = self.object.get_content()

        return context


special_coverage = SpecialCoverageView.as_view()
