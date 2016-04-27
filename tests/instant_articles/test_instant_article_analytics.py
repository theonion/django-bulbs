from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

class AnalyticsViewTests(TestCase):
    def test_analytics(self):
        self.client = Client()

        url = reverse("instant_article_analytics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Instant Articles", response.context_data.get("platform"))
