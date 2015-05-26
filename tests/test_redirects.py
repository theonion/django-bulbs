import urlparse

from django.core.urlresolvers import reverse
from django.test import Client

from bulbs.utils.test import BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class RedirectTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(RedirectTestCase, self).setUp()
        self.test_obj = TestContentObj.objects.create(title="Testing redirects")

    def test_simple_redirect(self):
        client = Client()
        endpoint = reverse("utm-redirect-pk", kwargs={"pk": self.test_obj.id})
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 301)
        parsed = urlparse.urlparse(response["Location"])
        self.assertEqual(parsed.path, self.test_obj.get_absolute_url())

    def test_utm_redirect(self):
        client = Client()
        endpoint = reverse("utm-redirect-tracking",
                           kwargs={
                               "pk": self.test_obj.id,
                               "source": "tsd",
                               "medium": "",
                               "name": ""
                           })
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 301)

        parsed = urlparse.urlparse(response["Location"])
        self.assertEqual(parsed.path, self.test_obj.get_absolute_url())

        qs = urlparse.parse_qs(parsed.query)
        expected_qs = {
            "utm_source": ["twitter"],
            "utm_medium": ["ShareTools"],
            "utm_campaign": ["default"]}
        self.assertEqual(expected_qs, qs)
