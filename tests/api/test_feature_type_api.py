from django.core.urlresolvers import reverse
from django.test.client import Client

from tests.utils import BaseAPITestCase

from bulbs.content.models import FeatureType


class FeatureTypeApiTestCase(BaseAPITestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def test_tag_api_search(self):
        FeatureType.objects.create(name="Blergh")
        FeatureType.objects.create(name="Blech")
        FeatureType.objects.create(name="Blemish")

        client = Client()
        client.login(username="admin", password="secret")

        response = client.get(reverse("feature-type-list"), content_type="application/json")
        self.assertEqual(len(response.data), 3)

        response = client.get(reverse("feature-type-list"), {"search": "blec"}, content_type="application/json")
        self.assertEqual(len(response.data), 1)
