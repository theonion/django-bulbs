import json

from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.views.generic import ListView
from django.shortcuts import render

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
        types = self.types or self.kwargs.get('types') or request.GET.get('type', [])
        published = self.published or self.kwargs.get('published') or self.request.GET.get('published', [])
        return Contentish.search(tags=tags, types=types, published=published)

    # def get(self, request, *args, **kwargs):
    #     tags = self.tags or kwargs.get('tags') or request.GET.get('tags')
    #     content_type = self.content_type or kwargs.get('content_type') or request.GET.get('content_type')
    #     published = self.published or kwargs.get('published') or request.GET.get('published')

    #     queryset = Content.objects.search(tags=tags, content_type=content_type, published=published)
    #     paginator = self.paginator_class(queryset, 25)

    #     page = self.kwargs.get('page') or self.request.GET.get('page') or 1
    #     try:
    #         page_number = int(page)
    #     except ValueError:
    #         if page == 'last':
    #             page_number = paginator.num_pages
    #         else:
    #             raise Http404(u"Page is not 'last', nor can it be converted to an int.")
    #     try:
    #         page = paginator.page(page_number)
    #     except InvalidPage:
    #         raise Http404(u'Invalid page (%s' % page_number)

    #     context = {
    #         'paginator': paginator,
    #         'page_obj': page,
    #         'is_paginated': page.has_other_pages(),
    #         'object_list': page.object_list
    #     }

    #     return None
