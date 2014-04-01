import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client
from django.utils import timezone

from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.content.models import LogEntry

from tests.testcontent.models import TestContentObj


class ContentAPITestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(ContentAPITestCase, self).setUp()
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

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


class TestPublishContentAPI(ContentAPITestCase):
    """Base class to test updates on `Content` subclasses."""

    def test_publish_now(self):

        content = TestContentObj.objects.create(
            title="Django Unchained: How a framework tried to run using async IO",
            description="Spoiler alert: it didn't go great, unless you measure by the number of HN articles about it",
            foo="SUCK IT, NERDS."
        )

        client = Client()
        client.login(username="admin", password="secret")

        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        # ensure it was created and got an id
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "published")

        # assert that we can load it up
        article = TestContentObj.objects.get(id=content.id)
        self.assertIsNotNone(article.published)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="published")

    def test_publish_specific(self):

        content = TestContentObj.objects.create(
            title="Django Unchained: How a framework tried to run using async IO",
            description="Spoiler alert: it didn't go great, unless you measure by the number of HN articles about it",
            foo="SUCK IT, NERDS."
        )

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": "2013-06-09T00:00:00-06:00"}),
            content_type="application/json")

        # ensure it was created and got an id
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "published")

        # assert that we can load it up
        article = TestContentObj.objects.get(id=content.id)
        self.assertEqual(article.published.year, 2013)
        self.assertEqual(article.published.month, 6)
        self.assertEqual(article.published.day, 9)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="published")

    def test_unpublish(self):
        content = TestContentObj.objects.create(
            title="Django Unchained: How a framework tried to run using async IO",
            description="Spoiler alert: it didn't go great, unless you measure by the number of HN articles about it",
            foo="SUCK IT, NERDS.",
            published=timezone.now()
        )

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": False}),
            content_type="application/json")
        # ensure it was created and got an id
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "draft")

        # assert that we can load it up
        article = TestContentObj.objects.get(id=content.id)
        self.assertEqual(article.published, None)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="draft")

