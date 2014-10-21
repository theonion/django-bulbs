import logging

from bulbs.content.models import Content, ObfuscatedUrlInfo

from django.conf import settings
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
from django.views.generic import ListView, DetailView

logger = logging.getLogger(__name__)


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

        return Content.search_objects.search(**search_kwargs)


class BaseContentDetailView(DetailView):
    """Should be used as the base for all content detail views."""

    model = Content
    context_object_name = "content"
    redirect_correct_path = True  # By default, we'll redirect the user to the proper URL

    def token_from_kwargs(self, request_kwargs):
        """Normalized way to retrieve token from request kwargs. Use this in custom GET
        implementations if this detail view should be accessible via token."""
        self.token = request_kwargs.get("token", None)

    def get(self, request, *args, **kwargs):
        """Override default get function to use token if there is one to retrieve object. If a
        subclass should use their own GET implementation, token_from_kwargs should be called if
        that detail view should be accessible via token."""
        
        # check if we have a token argument from incoming url, assign it so self.get_object can use
        #   the token to retrieve the proper object. Has to be done this way, otherwise DetailView
        #   expects a slug and/or pk to be provided by url pattern.
        self.token_from_kwargs(kwargs)
        
        self.object = self.get_object()

        # We only want to redirect is that setting is true, and we don't have a token
        if self.redirect_correct_path and self.token is None:

            # Also we obviously only want to redirect if the URL is wrong
            if self.request.path != self.object.get_absolute_url():
                return HttpResponsePermanentRedirect(self.object.get_absolute_url())

        context = self.get_context_data(object=self.object)
        response = self.render_to_response(context)

        if self.object.published is None or self.object.published > timezone.now():
            if not request.user.is_staff and self.token is None:
                redirect_unpublished = getattr(settings, "REDIRECT_UNPUBLISHED_TO_LOGIN", True)
                if not request.user.is_authenticated() and redirect_unpublished:
                    next_url = self.object.get_absolute_url()
                    response = HttpResponseRedirect("{}?next={}".format(settings.LOGIN_URL, next_url))
                else:
                    raise Http404
            add_never_cache_headers(response)
        else:
            response["Vary"] = "Accept-Encoding"

        return response

    def get_object(self, queryset=None):
        """Override default get_object to retrieve object from token if available."""

        # check if we have a token assigned (should be assigned by get function)
        if self.token is not None:
            try:
                # we have a token here, attempt to use it to retrieve object it references
                info = ObfuscatedUrlInfo.objects.get(url_uuid=self.token)

                now = timezone.now()
                if info.create_date <= now and now < info.expire_date:
                    # we are in the provided date window, return referenced content
                    return info.content
                else:
                    # date doesn't match, don't let user access
                    raise Http404("No content found matching UUID")

            except ObfuscatedUrlInfo.DoesNotExist:
                # could not find any url info matching provided uuid, 404
                raise Http404("No content found matching UUID")

        # no token was provided, use get_object() as normal
        return super(BaseContentDetailView, self).get_object()

content_list = ContentListView.as_view()
