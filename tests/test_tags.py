from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.content.models import Tag

from tests.testcontent.models import TestCategory


class TagTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(TagTestCase, self).setUp()
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_tag_api_search(self):
        Tag.objects.create(name="Blergh")
        Tag.objects.create(name="Blech")
        Tag.objects.create(name="Blemish")
        TestCategory.objects.create(name="Blended", baz="whatever")

        Tag.search_objects.refresh()
        TestCategory.search_objects.refresh()

        client = Client()
        client.login(username="admin", password="secret")

        response = client.get(reverse("tag-list"), {"search": "ble"}, content_type="application/json")
        self.assertEqual(response.data.get("count", 0), 4)

        response = client.get(reverse("tag-list"), {"search": "bler"}, content_type="application/json")
        self.assertEqual(response.data.get("count", 0), 1)

        response = client.get(reverse("tag-list"), {"types": "testcontent_testcategory", "search": "ble"}, content_type="application/json")
        self.assertEqual(response.data.get("count", 0), 1)

        response = client.get(reverse("tag-list"), {"types": "content_tag", "search": "ble"}, content_type="application/json")
        self.assertEqual(response.data.get("count", 0), 3)

        response = client.get(reverse("tag-list"), {"types": "testcontent_testcategory", "search": "bl"}, content_type="application/json")
        self.assertEqual(response.data.get("count", 0), 1)
