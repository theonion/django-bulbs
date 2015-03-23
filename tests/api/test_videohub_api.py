try:
    import json
except ImportError:
    import simplejson as json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

import requests


class VideoHubVideoViewSetTests(TestCase):

    SKIP_SEARCH = False

    def setUp(self):
        res = requests.get("http://videohub.local/")
        if not res.status_code == 200:
            self.SKIP_SEARCH = True
            return
        self.search_url = reverse("videohub-video-search-hub")
        self.client = Client()
        settings.VIDEOHUB_API_TOKEN = "Token 5bd1421dc4b162426bfa551e2b9c3e8407758820"

    def test_search(self):
        if self.SKIP_SEARCH:
            return
        payload = {"query": "wolf"}
        res = self.client.post(self.search_url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        content = res.data
        self.assertIn("facets", content)
        self.assertIn("counts", content)
        self.assertIn("results", content)
