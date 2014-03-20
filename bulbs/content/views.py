from django.views.generic import ListView

from bulbs.content.models import Content


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
            tags = self.kwargs['tags']
            if not isinstance(tags, list):
                tags = [tags]
            search_kwargs['tags'] = tags
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

        return Content.search_objects.search(**search_kwargs)


content_list = ContentListView.as_view()
