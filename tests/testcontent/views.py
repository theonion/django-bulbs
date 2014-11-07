from bulbs.content.views import BaseContentDetailView, ContentListView

from .models import TestContentObjTwo


class AllContentListView(ContentListView):
    template_name = "testapp/content_list.html"


class ContentTwoListView(ContentListView):
    model = TestContentObjTwo
    template_name = "testapp/content_list.html"


class TestContentDetailView(BaseContentDetailView):
    """Test ContentDetailView that is based on the BaseContentDetailView as expected."""
    template_name = "testapp/testcontentobj_detail.html"


test_content_detail = TestContentDetailView.as_view()
test_all_content_list = AllContentListView.as_view()
test_content_two_list = ContentTwoListView.as_view()
