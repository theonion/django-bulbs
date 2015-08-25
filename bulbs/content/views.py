import logging

from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
from django.views.generic import ListView, DetailView, View

from bulbs.content.custom_search import custom_search_model
from bulbs.content.models import Content, ObfuscatedUrlInfo

logger = logging.getLogger(__name__)


class ContentListView(ListView):
    model = Content

    feature_types = None
    tags = None
    types = None
    published = None
    before = None
    after = None

    allow_empty = True
    paginate_by = 20
    context_object_name = "content_list"
    template_name = None

    def get_queryset(self):
        search_kwargs = {}
        if "tags" in self.request.GET:
            search_kwargs["tags"] = self.request.GET.getlist("tags", [])
        elif "tag" in self.request.GET:
            search_kwargs["tags"] = self.request.GET.getlist("tag", [])

        if "tags" in self.kwargs:
            tags = self.kwargs["tags"]
            if not isinstance(tags, list):
                tags = [tags]
            search_kwargs["tags"] = tags
        try:
            if self.tags > 0:
                search_kwargs["tags"] = self.tags
        except TypeError:
            pass

        if "types" in self.request.GET:
            search_kwargs["types"] = self.request.GET.getlist("types", [])
        elif "type" in self.request.GET:
            search_kwargs["types"] = self.request.GET.getlist("type", [])

        if "types" in self.kwargs:
            search_kwargs["types"] = self.kwargs["types"]

        try:
            if self.types > 0:
                search_kwargs["types"] = self.types
        except TypeError:
            pass

        if "feature_types" in self.request.GET:
            search_kwargs["feature_types"] = self.request.GET.getlist("feature_types", [])
        elif "feature_type" in self.request.GET:
            search_kwargs["feature_types"] = self.request.GET.getlist("feature_type", [])

        if "feature_types" in self.kwargs:
            search_kwargs["feature_types"] = self.kwargs["feature_types"]
        try:
            if self.feature_types > 0:
                search_kwargs["feature_types"] = self.feature_types
        except TypeError:
            pass

        if "published" in self.kwargs:
            search_kwargs["published"] = self.kwargs["published"]
        if self.published:
            search_kwargs["published"] = self.published

        if "before" in self.request.GET:
            search_kwargs["before"] = self.request.GET["before"]
        if "before" in self.kwargs:
            search_kwargs["before"] = self.kwargs["before"]
        if self.before:
            search_kwargs["before"] = self.before

        if "after" in self.request.GET:
            search_kwargs["after"] = self.request.GET["after"]
        if "after" in self.kwargs:
            search_kwargs["after"] = self.kwargs["after"]
        if self.after:
            search_kwargs["after"] = self.after

        if "q" in self.request.GET:
            search_kwargs["query"] = self.request.GET["q"]

        return self.model.search_objects.search(**search_kwargs)


class PaginatedMixin(object):

    def get_context_data(self, **kwargs):
        context = super(PaginatedMixin, self).get_context_data(**kwargs)

        params = self.request.GET.copy()
        page = context.get("page_obj")
        if page:
            if page.has_next():
                params["page"] = page.next_page_number()
                context["next_url"] = u"{0}?{1}".format(self.request.path, params.urlencode())
            if page.has_previous():
                params["page"] = page.previous_page_number()
                context["previous_url"] = u"{0}?{1}".format(self.request.path, params.urlencode())

        return context


class ContentCustomSearchListView(ListView):
    model = Content
    paginate_by = 20
    context_object_name = "content_list"
    is_preview = False
    is_published = True
    field_map = {
        "feature-type": "feature_type.slug",
        "tag": "tags.slug",
        "content-type": "_type"
    }

    def get_queryset(self):
        query = self.get_search_query()
        return self.get_custom_search_queryset(query)

    def get_search_query(self):
        return {}

    def get_custom_search_queryset(self, query):
        qs = custom_search_model(
            self.model, query, preview=self.is_preview,
            published=self.is_published, field_map=self.field_map
        )
        return qs


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
content_custom_search_list = ContentCustomSearchListView.as_view()
