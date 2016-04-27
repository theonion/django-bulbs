from bulbs.utils.test import BaseIndexableTestCase

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

class InstantArticleAdViewTests(TestCase):
    def setUp(self):
        super(InstantArticleAdViewTests, self).setUp()
        self.client = Client()
        self.url = reverse("instant_article_ad")

    def test_ad_unit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('<div class="dfp dfp-slot-instant-article-inread" data-ad-unit="instant-article-inread" >', str(response.content))
