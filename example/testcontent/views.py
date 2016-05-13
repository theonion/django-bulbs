import json

from bulbs.content.views import BaseContentDetailView, ContentListView, ContentCustomSearchListView

from .models import TestContentObjTwo


class AllContentListView(ContentListView):
    template_name = "testapp/content_list.html"


class ContentTwoListView(ContentListView):
    model = TestContentObjTwo
    template_name = "testapp/content_list.html"


class TestContentCustomSearchListView(ContentCustomSearchListView):
    template_name = "testapp/content_list.html"

    def post(self, *args, **kwargs):
        """Allow POST for those big queries."""
        return self.get(*args, **kwargs)

    def get_search_query(self):
        params = json.loads(self.request.body.decode("utf8"))
        query = params.get("query", {})
        return query


class TestContentDetailView(BaseContentDetailView):
    """Test ContentDetailView that is based on the BaseContentDetailView as expected."""
    template_name = "testapp/testcontentobj_detail.html"


test_content_detail = TestContentDetailView.as_view()
test_all_content_list = AllContentListView.as_view()
test_content_two_list = ContentTwoListView.as_view()
test_published_content_custom_search_list = TestContentCustomSearchListView.as_view()
test_unpublished_content_custom_search_list = TestContentCustomSearchListView.as_view(is_published=False)
