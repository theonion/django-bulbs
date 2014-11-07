import logging

from bulbs.content.models import Content, ObfuscatedUrlInfo

from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
from django.views.generic import ListView, DetailView, View

logger = logging.getLogger(__name__)


class ContentListView(ListView):
    model = Content

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
            search_kwargs['feature_types'] = self.request.GET.getlist(
                'feature_types', [])
        elif 'feature_type' in self.request.GET:
            search_kwargs['feature_types'] = self.request.GET.getlist(
                'feature_type', [])

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

        return self.model.search_objects.search(**search_kwargs)


class BaseContentDetailView(DetailView):
    """Should be used as the base for all content detail views."""

    model = Content
    context_object_name = "content"
    redirect_correct_path = True  # By default, we'll redirect the user to the proper URL

    def get(self, request, *args, **kwargs):
        """Override default get function to use token if there is one to retrieve object. If a
        subclass should use their own GET implementation, token_from_kwargs should be called if
        that detail view should be accessible via token."""
        
        self.object = self.get_object()

        allow_anonymous = kwargs.get("allow_anonymous", False)

        # We only want to redirect is that setting is true, and we're not allowing anonymous users
        if self.redirect_correct_path and not allow_anonymous:

            # Also we obviously only want to redirect if the URL is wrong
            if self.request.path != self.object.get_absolute_url():
                return HttpResponsePermanentRedirect(self.object.get_absolute_url())

        context = self.get_context_data(object=self.object)
        response = self.render_to_response(context)

        # If we have an unpublished article....
        if self.object.published is None or self.object.published > timezone.now():

            # And the user doesn't have permission to view this
            if not request.user.is_staff and not allow_anonymous:
                redirect_unpublished = getattr(settings, "REDIRECT_UNPUBLISHED_TO_LOGIN", True)
                if not request.user.is_authenticated() and redirect_unpublished:
                    next_url = self.object.get_absolute_url()
                    response = HttpResponseRedirect("{}?next={}".format(settings.LOGIN_URL, next_url))
                else:
                    raise Http404

            # Never cache unpublished articles
            add_never_cache_headers(response)
        else:
            response["Vary"] = "Accept-Encoding"

        return response


class UnpublishedContentView(View):

    def dispatch(self, request, *args, **kwargs):
        
        token = kwargs.get("token", None)
        info = get_object_or_404(ObfuscatedUrlInfo, url_uuid=token)

        now = timezone.now()
        if info.create_date >= now or now > info.expire_date:
            # date doesn't match, don't let user access
            raise Http404("No content found matching UUID")

        try:
            view, args, kwargs = resolve(info.content.get_absolute_url())
        except Resolver404:
            raise Http404("No content found matching UUID")

        kwargs["request"] = request
        kwargs["allow_anonymous"] = True
        return view(*args, **kwargs)


unpublished = UnpublishedContentView.as_view()
content_list = ContentListView.as_view()
