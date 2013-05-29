import json

from django.http import HttpResponse
from django.views.generic import ListView

from bulbs.base.models import Contentish, Tagish


def render_json(page):
    data = {'object_list': [obj.to_dict() for obj in page.object_list]}
    return HttpResponse(json.dumps(data), content_type="application/json")


def search_tags(request):
    tags = Tagish.search(request.GET.get('q'))
    tag_data = [tag.name for tag in tags]
    return HttpResponse(json.dumps(tag_data), content_type='application/json')


class ContentListView(ListView):

    tags = []
    types = []
    published = None

    allow_empty = True
    paginate_by = 20
    context_object_name = 'content'
    template_name = None

    renderers = {
        "text/html": "html",
        "application/json": render_json
    }

    def get_renderer(self, request):
        for mime_type in self.renderers:
            pass

    def get_queryset(self):
        tags = self.tags or self.kwargs.get('tags') or self.request.GET.getlist('tag', [])
        types = self.types or self.kwargs.get('types') or self.request.GET.get('type', [])
        published = self.published or self.kwargs.get('published') or self.request.GET.get('published', [])
        return Contentish.search(tags=tags, types=types, published=published)
