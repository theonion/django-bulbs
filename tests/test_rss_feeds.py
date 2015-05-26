from django.core.urlresolvers import reverse
from django.test.client import Client
from bulbs.utils.test import BaseIndexableTestCase

from bulbs.utils.test import make_content


class RSSTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def test_rss_feed(self):
        # Let's bust out some content
        make_content(_quantity=100)

        rss_endpoint = reverse("rss-feed")

        client = Client()
        response = client.get(rss_endpoint)
        self.assertEqual(response.status_code, 200)
