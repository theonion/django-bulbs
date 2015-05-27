from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase, make_content

from example.testcontent.models import TestContentObj


class RSSTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def test_rss_feed(self):
        # Let's bust out some content
        make_content(TestContentObj, published=timezone.now() - timedelta(hours=2), _quantity=35)
        TestContentObj.search_objects.refresh()

        rss_endpoint = reverse("rss-feed")

        client = Client()
        response = client.get(rss_endpoint)
        self.assertEqual(response.status_code, 200)

        first_item = response.context["page_obj"].object_list[0]
        self.assertTrue(hasattr(first_item, "feed_url"))
