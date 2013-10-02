import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils import simplejson as json
from django.views.generic import CreateView, ListView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

from elasticutils import S

from bulbs.content.models import Content, Tag


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

    allow_empty = True
    paginate_by = 20
    context_object_name = 'content_list'
    template_name = None

    def get_queryset(self):
        search_kwargs = {}
        if 'tags' in self.request.GET:
            search_kwargs['tags'] = self.request.GET.getlist('tags', [])
        if 'tags' in self.kwargs:
            search_kwargs['tags'] = self.kwargs['tags']
        if self.tags > 0:
            search_kwargs['tags'] = self.tags

        if 'types' in self.request.GET:
            search_kwargs['types'] = self.request.GET.getlist('types', [])
        if 'types' in self.kwargs:
            search_kwargs['types'] = self.kwargs['types']
        if self.types > 0:
            search_kwargs['types'] = self.types

        if 'feature_types' in self.request.GET:
            search_kwargs['feature_types'] = self.request.GET.getlist('feature_types', [])
        if 'feature_types' in self.kwargs:
            search_kwargs['feature_types'] = self.kwargs['feature_types']
        if self.feature_types > 0:
            search_kwargs['feature_types'] = self.feature_types

        if 'published' in self.kwargs:
            search_kwargs['published'] = self.kwargs['published']
        if self.published:
            search_kwargs['published'] = self.published

        return Content.objects.search(**search_kwargs)


content_list = ContentListView.as_view()


class PolymorphicContentFormMixin(object):
    _form_cache = {}

    def get_polymorphic_content_form_class(self, model_class):
        from django import forms

        try:
            form_class = self._form_cache[model_class]
        except KeyError:
            class DoctypeModelForm(forms.ModelForm):
                class Meta:
                    model = model_class
                    exclude = ['authors', 'image']
            form_class = DoctypeModelForm
            self._form_cache[model_class] = form_class

        return form_class


class ContentCreateView(PolymorphicContentFormMixin, CreateView):
    model = Content
 
    def get_form_class(self):
        """Return a `ModelForm` based on the request `doctype` parameter."""
        try:
            doctype_name = self.request.REQUEST['doctype']
        except KeyError:    
            raise Http404('Create view needs a doctype parameter')
        try:
            doctype_class = self.model.get_doctypes()[doctype_name]
        except KeyError:
            raise Http404('Doctype "%s" not found :(' % doctype_name)

        return self.get_polymorphic_content_form_class(doctype_class)


class ContentUpdateView(PolymorphicContentFormMixin, UpdateView):
    model = Content

    def get_form_class(self):
        # The polymorphic query retrieved the true subclass
        real_model_class = self.object.__class__
        return self.get_polymorphic_content_form_class(real_model_class)


class ContentTagManagementView(SingleObjectMixin, View):
    """A view for managing the tags for a given `Content` item."""
    model = Content

    def get(self, *args, **kwargs):
        """Return all tags for a piece of content."""
        #super(ContentTagManagementView, self).get(*args, **kwargs)
        content = self.get_object()
        tag_data = [
            {'name': tag.name, 'slug': tag.slug} for tag in content.tags.all()
        ]
        return self.json_response(tag_data)

    def post(self, *args, **kwargs):
        """Adds a tag to a content item.""" 
        tag_name = self.get_tag_name()
        content = self.get_object()
        tag, created_tag = Tag.objects.get_or_create(name=tag_name)
        content.tags.add(tag)
        return self.json_response(dict(name=tag.name, slug=tag.slug))

    def delete(self, *args, **kwargs):
        """Removes a tag from a content item."""
        tag_name = self.get_tag_name()
        content = self.get_object()
        content.tags.all().filter(name=tag_name).delete()
        return HttpResponse('Ok')

    def json_response(self, data):
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_tag_name(self):
        """Pulls the tag name out of the request."""
        try:
            tag_name = self.request.REQUEST['tag']
        except KeyError:
            raise Http404('No tag provided.')
        tag_name = tag_name.strip()
        if not tag_name:
            return Http404('Tag name is empty.')
        return tag_name


manage_content_tags = ContentTagManagementView.as_view()
