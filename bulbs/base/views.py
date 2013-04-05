import json

from django.views import View
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render

from bulbs.base.models import Content


def render_json(page):
    data = {'object_list': [obj.to_dict() for obj in page.object_list]}
    return HttpResponse(json.dumps(data), content_type="application/json")


class ContentListView(View):

    tags = None
    content_type = None
    published = None

    allow_empty = True
    paginator_class = Paginator
    context_object_name = None
    template_name = None

    renderers = {
        "text/html": "html",
        "application/json": render_json
    }

    def get_renderer(self, request):
        for mime_type in self.renderers:
            pass

    def get(self, request, *args, **kwargs):
        tags = self.tags or kwargs.get('tags') or request.GET.get('tags')
        content_type = self.content_type or kwargs.get('content_type') or request.GET.get('content_type')
        published = self.published or kwargs.get('published') or request.GET.get('published')

        queryset = Content.objects.search(tags=tags, content_type=content_type, published=published)
        paginator = self.paginator_class(queryset, 25)

        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(u"Page is not 'last', nor can it be converted to an int.")
        try:
            page = paginator.page(page_number)
        except InvalidPage:
            raise Http404(u'Invalid page (%s' % page_number)

        context = {
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': page.has_other_pages(),
            'object_list': page.object_list
        }



        return None
