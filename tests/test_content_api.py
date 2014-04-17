import json
import datetime

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client
from django.utils import timezone

from elastimorphic.tests.base import BaseIndexableTestCase
from pyelasticsearch.client import JsonEncoder
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from bulbs.content.models import LogEntry, Tag, Content
from bulbs.content.serializers import TagSerializer
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

class TestContentListingAPI(ContentAPITestCase):
    """Test the listing of content"""

    def setUp(self):
        super(TestContentListingAPI, self).setUp()
        for i in range(47):
            TestContentObj.objects.create(
                title="Testing published content {}".format(i),
                description="Doesn't matter what it is, AS LONG AS IT GETS CLICKZ",
                foo="SUCK IT, NERDS.",
                published=timezone.now() - datetime.timedelta(hours=1)
            )

        for i in range(32):
            TestContentObj.objects.create(
                title="Testing published content {}".format(i),
                description="Doesn't matter what it is, AS LONG AS IT GETS CLICKZ",
                foo="SUCK IT, NERDS.",
                published=timezone.now() + datetime.timedelta(hours=1)
            )

        for i in range(13):
            TestContentObj.objects.create(
                title="Testing published content {}".format(i),
                description="Doesn't matter what it is, AS LONG AS IT GETS CLICKZ",
                foo="SUCK IT, NERDS."
            )

        TestContentObj.search_objects.refresh()

    def test_list_final(self):

        q = Content.search_objects.search(status="final")
        self.assertEqual(q.count(), 79)

        client = Client()
        client.login(username="admin", password="secret")

        response = client.get(reverse("content-list"), {"status": "final"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 79)
        self.assertEqual(len(response.data["results"]), 20)


class TestContentStatusAPI(ContentAPITestCase):

    def test_status_endpoint(self):
        content = TestContentObj.objects.create(
            title="Unpublished article"
        )
        client = Client()
        client.login(username="admin", password="secret")
        response = client.get(reverse("content-status", kwargs={"pk": content.id}), content_type="application/json")
        self.assertEqual(response.data["status"], "draft")

        content.published = timezone.now() - datetime.timedelta(hours=1)
        content.save()
        response = client.get(reverse("content-status", kwargs={"pk": content.id}), content_type="application/json")
        self.assertEqual(response.data["status"], "final")


class TestCreateContentAPI(ContentAPITestCase):
    """Test the creation of content strictly throught he API endpoint, ensuring
    that it ends up searchable"""

    def test_create_article(self):
        data = {
            "title": "Test Article",
            "description": "Testing out things with an article.",
            "foo": "Fighters",
            "image": {
                "id": 12345,
                "alt": None,
                "caption": None
            }
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
        self.assertEqual(response_data["status"], "final")

        # assert that we can load it up
        article = TestContentObj.objects.get(id=content.id)
        self.assertIsNotNone(article.published)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="final")

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
        self.assertEqual(response_data["status"], "final")

        # assert that we can load it up
        article = TestContentObj.objects.get(id=content.id)
        self.assertEqual(article.published.year, 2013)
        self.assertEqual(article.published.month, 6)
        self.assertEqual(article.published.day, 9)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="final")

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


class BaseUpdateContentAPI(ContentAPITestCase):
    """Base class to test updates on `Content` subclasses."""
    def setUp(self):
        super(BaseUpdateContentAPI, self).setUp()
        self.create_content()

    def create_content(self):
        """Override to create your own content here."""
        self.content = None
        raise NotImplementedError("Your test must override `create_content`")

    def updated_data(self):
        raise NotImplementedError("Your test must override `updated_data`")
        return {}

    def check_response_data(self, response_data, expected_data):
        for key in expected_data:
            self.assertEqual(response_data[key], expected_data[key])

    def _test_update_content(self):
        """Fetches an existing Content object and updates that sucker."""
        client = Client()
        client.login(username="admin", password="secret")
        new_data = self.updated_data()
        # TODO: use reverse there, Von Neumann
        content_detail_url = reverse("content-detail", kwargs={"pk": self.content.id})

        response = client.get(content_detail_url)
        self.assertEqual(response.status_code, 200)
        # Squirt in some new data
        content_data = response.data
        content_data.update(new_data)
        # PUT it up
        data = json.dumps(content_data, cls=JsonEncoder)
        response = client.put(content_detail_url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        # Check that it returns an instance with the new data
        # And check that the detail view is also correct
        response = client.get(content_detail_url)
        self.assertEqual(response.status_code, 200)
        self.check_response_data(response.data, new_data)


class TestUpdateContentAPI(BaseUpdateContentAPI):
    """Tests updating an `Article`"""
    def create_content(self):
        self.content = TestContentObj.objects.create(
            title="Booyah: The Cramer Story",
            description="Learn how one man booyahed his way to the top.",
            foo="booyah"
        )

    def updated_data(self):
        return dict(
            title="Cramer 2: Electric Booyah-loo",
            foo="whatta guy....booyah indeed!"
        )

    def test_update_article(self):
        self._test_update_content()


class TestAddTagsAPI(BaseUpdateContentAPI):
    """Tests adding `Tag` objects to an `Article`"""
    def create_content(self):
        self.tags = []
        for tag_name in ("TV", "Helicopters", "America"):
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            self.tags.append(tag)

        self.content = TestContentObj.objects.create(
            title="Adam Wentz reviews \"AirWolf\" (but it's not really a review anymore)",
            description="Learn what to think about the classic Donald P. Bellisario TV series",
            foo="What a show! What a helicopter!",
        )
      #  self.content.tags.add(self.tags[0])

    def updated_data(self):
        serializer = TagSerializer(self.tags, many=True)
        return dict(
            foo="Incredible! A helicopter/wolf hybrid that will blow your pants off!",
            tags=serializer.data
        )

    def test_update_tags(self):
        self._test_update_content()

    def check_response_data(self, response_data, expected_data):
        for key in expected_data:
            if key == "tags":
                try:
                    response_tag_ids = [tag["id"] for tag in response_data[key]]
                except TypeError:
                    response_tag_ids = [tag for tag in response_data[key]]
                self.assertEqual(response_tag_ids, response_tag_ids)
            else:
                self.assertEqual(response_data[key], expected_data[key])


class TestTrashContentAPI(ContentAPITestCase):
    def test_trash(self):
        content = TestContentObj.objects.create(
            title="Test Article",
            description="Testing out trash.",
            foo="Lorem ipsum dolor, oh myyyy!"
        )
        self.assertTrue(content.indexed)
        data = self.es.get(content.get_index_name(), content.get_mapping_type_name(), content.id)
        self.assertEqual(data["_source"]["title"], "Test Article")

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-trash", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        content = Content.objects.get(id=content.id)
        self.assertFalse(content.indexed)

        # check for a log
        LogEntry.objects.filter(object_id=content.pk).get(change_message="Trashed")

        with self.assertRaises(ElasticHttpNotFoundError):
            self.es.get(content.get_index_name(), content.get_mapping_type_name(), content.id)

        content.save()
        with self.assertRaises(ElasticHttpNotFoundError):
            self.es.get(content.get_index_name(), content.get_mapping_type_name(), content.id)

    def test_trash_404(self):
        client = Client()
        client.login(username="admin", password="secret")
        content = TestContentObj.objects.create(
            title="Test Article",
            description="Testing out trash.",
            foo="Lorem ipsum dolor, oh myyyy!"
        )
        content_rest_url = reverse("content-trash", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 404)
