from django.conf import settings
from django.db.models.loading import get_model
from django.utils import timezone
from django.views.decorators.cache import cache_control

from bulbs.content.views import BaseContentDetailView

LiveBlogModel = get_model(settings.BULBS_LIVEBLOG_MODEL)


class LiveblogNewEntriesView(BaseContentDetailView):
    model = LiveBlogModel
    template_name = 'liveblog/new_entries.html'
    redirect_correct_path = False

    def get_context_data(self, object):
        context = {}
        if 'entry_ids' not in self.request.GET:
            raise ValueError('param "entry_ids" MUST be specified')
        parsed_entry_ids = [x.strip() for x in self.request.GET['entry_ids'].split(',')]
        context['entries'] = self.object.entries.filter(
            pk__in=parsed_entry_ids,
            published__lte=timezone.now())
        return context

liveblog_new_entries = cache_control(max_age=600)(LiveblogNewEntriesView.as_view())
