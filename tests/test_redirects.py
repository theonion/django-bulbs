import urlparse

from django.test import Client

from elastimorphic.tests.base import BaseIndexableTestCase

from tests.testcontent.models import TestContentObj


class RedirectTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(RedirectTestCase, self).setUp()
        self.test_obj = TestContentObj.objects.create(title="Testing redirects")

    def test_simple_redirect(self):
        client = Client()
        response = client.get("/r/{}".format(self.test_obj.id))
        self.assertEqual(response.status_code, 301)
        parsed = urlparse.urlparse(response["Location"])
        self.assertEqual(parsed.path, self.test_obj.get_absolute_url())

    def test_utm_redirect(self):
        client = Client()
        response = client.get("/r/{}tsd".format(self.test_obj.id))
        self.assertEqual(response.status_code, 301)

        parsed = urlparse.urlparse(response["Location"])
        self.assertEqual(parsed.path, self.test_obj.get_absolute_url())

        qs = urlparse.parse_qs(parsed.query)
        expected_qs = {
            "utm_source": ["twitter"],
            "utm_medium": ["ShareTools"],
            "utm_campaign": ["default"]}
        self.assertEqual(expected_qs, qs)
