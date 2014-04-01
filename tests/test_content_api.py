import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client

from elastimorphic.tests.base import BaseIndexableTestCase

from tests.testcontent.models import TestContentObj, TestContentObjTwo


class ContentAPITestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(ContentAPITestCase, self).setUp()
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()
        self.content_rest_url = reverse("content-list")

        # reverse("content-detail")


class TestCreateContentAPI(ContentAPITestCase):
    """Test the creation of content strictly throught he API endpoint, ensuring
    that it ends up searchable"""

    def test_create_article(self):
        data = {
            "title": "Test Article",
            "description": "Testing out things with an article.",
            "foo": "Fighters",
        }
        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-list") + "?doctype=testcontent_testcontentobj"
        response = client.post(content_rest_url, json.dumps(data), content_type="application/json")
        # ensure it was created and got an id
        self.assertEqual(response.status_code, 201)  # 201 Created
        response_data = response.data
        self.assertIn("id", response_data, data)
        # check that all the fields went through
        for key in data:
            self.assertEqual(response_data[key], data[key])

        # assert that we can load it up
        article = TestContentObj.objects.get(id=response_data["id"])
        self.assertEqual(article.slug, slugify(data["title"]))

        # check for a log
        # LogEntry.objects.filter(object_id=article.pk).get(change_message="Created")
        
        # Make sure the article got refreshed
        TestContentObj.search_objects.refresh()

        # shows up in the list?
        response = client.get(reverse("content-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
