import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic import CreateView, ListView

from elasticutils import S

from bulbs.content.models import Content, Tag


def search_tags(request):
    tags = Tag.search(name=request.GET.get('q'))
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

    feature_types = []
    tags = []
    types = []
    published = None

    allow_empty = True
    paginate_by = 20
    context_object_name = 'content'
    template_name = None

    def get_queryset(self):
        pk = self.kwargs.get('pk') or self.request.GET.get('pk', None)
        tags = self.tags or self.kwargs.get('tags') or self.request.GET.getlist('tags', [])
        types = self.types or self.kwargs.get('types') or self.request.GET.getlist('types', [])
        feature_types = self.feature_types or self.kwargs.get('feature_types') or self.request.GET.getlist('feature_types', [])
        published = self.published or self.kwargs.get('published') or self.request.GET.get('published', [])
        return Content.search(
            pk=pk, tags=tags, feature_types=feature_types,
            types=types, published=published
        )

    def render_to_response(self, context, **response_kwargs):
        http_accept = self.request.META.get('HTTP_ACCEPT')
        if http_accept == 'application/json':
            data = {
                'count': context['paginator'].count,
                'num_pages': context['paginator'].num_pages,
                'page': {
                    # Page methods
                    'has_next': context['page_obj'].has_next(),
                    'has_previous': context['page_obj'].has_previous(),
                    'has_other_pages': context['page_obj'].has_other_pages(),
                    'start_index': context['page_obj'].start_index(),
                    'end_index': context['page_obj'].end_index(),
                    # Page attributes
                    'number': context['page_obj'].number
                },
            }
            data['results'] = [{
                'id': result.id,
                'slug': result.slug,
                'title': result.title,
                'description': result.description,
                'image': result.image_id,
                'byline': result.byline,
                'subhead': result.subhead,
                'published': result.published,
                'feature_type': result.feature_type} for result in context['object_list']]

            return HttpResponse(json.dumps(data), content_type='application/json')

        return super(ContentListView, self).render_to_response(context, **response_kwargs)


content_list = ContentListView.as_view()


class ContentCreateView(CreateView):
    model = Content
    _form_cache = {}

    def get_form_class(self):
        """Return a `ModelForm` based on the request `doctype` parameter."""
        from django import forms

        try:
            doctype_name = self.request.REQUEST['doctype']
        except KeyError:    
            raise Http404('Create view needs a doctype parameter')
        try:
            doctype_class = Content.get_doctypes()[doctype_name]
        except KeyError:
            raise Http404('Doctype "%s" not found :(' % doctype_name)

        # We have a valid doctype class, let's get a model form
        try:
            form_class = self._form_cache[doctype_name]
        except KeyError:
            class DoctypeModelForm(forms.ModelForm):
                class Meta:
                    model = doctype_class
                    exclude = ['authors', 'image']
            form_class = DoctypeModelForm
            self._form_cache[doctype_name] = form_class

        return form_class


