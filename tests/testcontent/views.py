from django.http import HttpResponse, Http404

from bulbs.content.views import BaseContentDetailView


class TestContentDetailView(BaseContentDetailView):
    """Test ContentDetailView that is based on the BaseContentDetailView as expected."""
    template_name = "testapp/testcontentobj_detail.html"
