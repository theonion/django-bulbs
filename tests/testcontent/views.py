from django.http import HttpResponse, Http404

from bulbs.content.views import BaseContentDetailView


class TestContentDetailView(BaseContentDetailView):
    """Test ContentDetailView that is based on the BaseContentDetailView as expected."""

    def get(self, request, *args, **kwargs):
        """Test GET function that will attempt to retrieve an article via token."""

        # we're overriding the base GET functionality, but we want to preserve token retrieval,
        #   so call token_from_kwargs function provided by base class to ensure get_object
        #   works correctly.
        self.token_from_kwargs(kwargs)

        # get object should now be able to use the token to find the correct content
        obj = self.get_object()

        if obj:
            return HttpResponse(obj.id)

        return Http404("Ah shoot, no object.")
