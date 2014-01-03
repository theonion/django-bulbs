import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils import simplejson as json
from django.views.generic import CreateView, ListView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

from elasticutils import S

from bulbs.content.models import Content, Tag

# TODO: shall we remove 'search_tags' and 'search_feature_types'?
def search_tags(request):
    tags = Tag.objects.search(name=request.GET.get('q'))
    tag_data = [{'name': tag.name, 'slug': tag.slug} for tag in tags]
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

    feature_types = None
    tags = None
    types = None
    published = None
    authors = None

    allow_empty = True
    paginate_by = 20
    context_object_name = 'content_list'
    template_name = None

    def get_queryset(self):
        search_kwargs = {}
        if 'tags' in self.request.GET:
            search_kwargs['tags'] = self.request.GET.getlist('tags', [])
        elif 'tag' in self.request.GET:
            search_kwargs['tags'] = self.request.GET.getlist('tag', [])

        if 'tags' in self.kwargs:
            search_kwargs['tags'] = self.kwargs['tags']
        if self.tags > 0:
            search_kwargs['tags'] = self.tags

        if 'types' in self.request.GET:
            search_kwargs['types'] = self.request.GET.getlist('types', [])
        elif 'type' in self.request.GET:
            search_kwargs['types'] = self.request.GET.getlist('type', [])

        if 'types' in self.kwargs:
            search_kwargs['types'] = self.kwargs['types']
        if self.types > 0:
            search_kwargs['types'] = self.types

        if 'feature_types' in self.request.GET:
            search_kwargs['feature_types'] = self.request.GET.getlist('feature_types', [])
        elif 'feature_type' in self.request.GET:
            search_kwargs['feature_types'] = self.request.GET.getlist('feature_type', [])

        if 'feature_types' in self.kwargs:
            search_kwargs['feature_types'] = self.kwargs['feature_types']
        if self.feature_types > 0:
            search_kwargs['feature_types'] = self.feature_types

        if 'published' in self.kwargs:
            search_kwargs['published'] = self.kwargs['published']
        if self.published:
            search_kwargs['published'] = self.published

        if 'authors' in self.request.GET:
            search_kwargs['authors'] = self.request.GET.getlist('authors', [])
        elif 'author' in self.request.GET:
            search_kwargs['authors'] = self.request.GET.getlist('author', [])
        if 'authors' in self.kwargs:
            search_kwargs['authors'] = self.kwargs['authors']
        if self.authors:
            search_kwargs['authors'] = self.authors

        if 'q' in self.request.GET:
            search_kwargs['query'] = self.request.GET['q']

        return Content.objects.search(**search_kwargs)


content_list = ContentListView.as_view()
