import json

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView

from elasticutils import S

from bulbs.content.models import Contentish, Tagish


def render_json(page):
    data = {'object_list': [obj.to_dict() for obj in page.object_list]}
    return HttpResponse(json.dumps(data), content_type="application/json")


def search_tags(request):
    tags = Tagish.search(request.GET.get('q'))
    tag_data = [tag.name for tag in tags]
    return HttpResponse(json.dumps(tag_data), content_type='application/json')


def search_feature_types(request):
    results = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES.get('default'))
    if 'q' in request.GET:
        results = results.query(feature_type__prefix=request.GET['q'])
    facet_counts = results.facet_raw(feature_type={'terms': {'field': 'feature_type.slug', 'size': 20}}).facet_counts()

    slug_facets = facet_counts['feature_type'][::2]
    names_facets = facet_counts['feature_type'][1::2]
    data = [{
        'slug': facet['term'],
        'count': facet['count']
    } for facet in slug_facets]
    for index, facet in enumerate(names_facets):
        data[index]['name'] = facet['term']

    return HttpResponse(json.dumps(data), content_type='application/json')


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
        types = self.types or self.kwargs.get('types') or self.request.GET.getlist('type', [])
        feature_types = self.types or self.kwargs.get('feature_types') or self.request.GET.getlist('feature_type', [])
        published = self.published or self.kwargs.get('published') or self.request.GET.get('published', [])
        return Contentish.search(tags=tags, feature_types=feature_types, types=types, published=published)
