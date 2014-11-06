import json
from datetime import datetime, timedelta

import elasticsearch
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client
from django.utils import timezone

from bulbs.content.models import LogEntry, Tag, Content, ObfuscatedUrlInfo
from tests.testcontent.models import TestContentObj, TestContentDetailImage
from tests.utils import JsonEncoder, BaseAPITestCase, make_content


class TestContentListingAPI(BaseAPITestCase):
    """Test the listing of content"""

    def setUp(self):
        super(TestContentListingAPI, self).setUp()
        for i in range(47):
            make_content(published=timezone.now() - timedelta(hours=1))

        for i in range(32):
            make_content(published=timezone.now() + timedelta(hours=1))

        for i in range(13):
            make_content(published=None)

        Content.search_objects.refresh()

    def test_list_final(self):

        q = Content.search_objects.search(status="final")
        self.assertEqual(q.count(), 79)

        client = Client()
        client.login(username="admin", password="secret")

        response = client.get(reverse("content-list"), {"status": "final"},
                              content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 79)
        self.assertEqual(len(response.data["results"]), 20)


class TestContentStatusAPI(BaseAPITestCase):
    def test_status_endpoint(self):
        content = make_content(published=None)
        client = Client()
        client.login(username="admin", password="secret")
        response = client.get(reverse("content-status", kwargs={"pk": content.id}),
                              content_type="application/json")
        self.assertEqual(response.data["status"], "draft")

        content.published = timezone.now() - timedelta(hours=1)
        content.save()
        response = client.get(reverse("content-status", kwargs={"pk": content.id}),
                              content_type="application/json")
        self.assertEqual(response.data["status"], "final")


class TestCreateContentAPI(BaseAPITestCase):
    """Test the creation of content strictly throught he API endpoint, ensuring
    that it ends up searchable"""

    def test_create_article(self):
        User = get_user_model()

        author = User.objects.create(
            username="csinchok",
            first_name="Chris",
            last_name="Sinchok"
        )
        data = {
            "title": "Test Article",
            "description": "Testing out things with an article.",
            "foo": "Fighters",
            "feature_type": "Some Super Long String Probably",
            "authors": [{
                            "id": author.id,
                            "username": author.username,
                            "email": "",
                            "full_name": "Chris Sinchok",
                            "short_name": "Chris",
                            "first_name": "Chris",
                            "last_name": "Sinchok"
                        }]
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
        self.assertEqual(article.feature_type.name, data["feature_type"])

        # check for a log
        # LogEntry.objects.filter(object_id=article.pk).get(change_message="Created")

        # Make sure the article got refreshed
        TestContentObj.search_objects.refresh()

        # shows up in the list?
        response = client.get(reverse("content-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)


class TestPublishContentAPI(BaseAPITestCase):
    """Base class to test updates on `Content` subclasses."""

    def test_publish_now(self):
        content = make_content(
            title="Django Unchained: How a framework tried to run using async IO",
            description="Spoiler alert: it didn't go great, unless you measure by the number of HN articles about it",
            foo="SUCK IT, NERDS.",
            published=None
        )

        client = Client()
        client.login(username="admin", password="secret")

        # ensure permission to publish
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # ok now it should work
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "final")

        # assert that we can load it up
        article = Content.objects.get(id=content.id)
        self.assertIsNotNone(article.published)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="final")

    def test_author_publish_permissions(self):
        content = make_content(published=None)
        content.authors.add(self.admin)

        client = Client()
        client.login(username="admin", password="secret")

        # ensure permission to publish
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.give_author_permissions()
        # ok now it should work
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "final")

        # assert that we can load it up
        article = Content.objects.get(id=content.id)
        self.assertIsNotNone(article.published)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="final")

    def test_publish_specific(self):
        content = make_content(published=None)

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": "2013-06-09T00:00:00-06:00"}),
            content_type="application/json")
        # no permissions, no publish
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # now it should work
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": "2013-06-09T00:00:00-06:00"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "final")

        # assert that we can load it up
        article = Content.objects.get(id=content.id)
        self.assertEqual(article.published.year, 2013)
        self.assertEqual(article.published.month, 6)
        self.assertEqual(article.published.day, 9)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="final")

    def test_unpublish(self):
        content = make_content(published=timezone.now())

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-publish", kwargs={"pk": content.id})
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": False}),
            content_type="application/json")
        # no permissions, no unpublish
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # now it should work
        response = client.post(
            content_rest_url,
            data=json.dumps({"published": False}),
            content_type="application/json")
        # ensure it was created and got an id
        self.assertEqual(response.status_code, 200)
        response_data = response.data
        self.assertEqual(response_data["status"], "draft")

        # assert that we can load it up
        article = Content.objects.get(id=content.id)
        self.assertEqual(article.published, None)
        # check for a log
        LogEntry.objects.filter(object_id=article.pk).get(change_message="draft")


class BaseUpdateContentAPI(BaseAPITestCase):
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

        content_detail_url = reverse("content-detail", kwargs={"pk": self.content.id})

        response = client.get(content_detail_url)
        self.assertEqual(response.status_code, 200)
        # Squirt in some new data
        content_data = response.data
        content_data.update(new_data)
        # PUT it up
        data = json.dumps(content_data, cls=JsonEncoder)
        response = client.put(content_detail_url, data=data, content_type="application/json")
        # no permissions, no PUTing
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # ok, PUT it now
        response = client.put(content_detail_url, data=data, content_type="application/json")
        if response.status_code != 200:
            print(response.content)
        self.assertEqual(response.status_code, 200)

        # Check that it returns an instance with the new data
        # And check that the detail view is also correct
        response = client.get(content_detail_url)
        self.assertEqual(response.status_code, 200)
        self.check_response_data(response.data, new_data)


class TestUpdateContentAPI(BaseUpdateContentAPI):
    """Tests updating an `Article`"""

    def create_content(self):
        self.content = make_content(TestContentObj, title="Booyah: The Cramer Story", foo="booyah")

    def updated_data(self):
        return dict(
            title="Cramer 2: Electric Booyah-loo",
            foo="whatta guy....booyah indeed!"
        )

    def test_update_article(self):
        self._test_update_content()


class TestUpdateAuthorsAPI(BaseUpdateContentAPI):
    """Tests updating an `Article`"""

    def create_content(self):
        User = get_user_model()
        self.author = User.objects.create(
            username="csinchok",
            first_name="Chris",
            last_name="Sinchok"
        )
        self.content = make_content(TestContentObj, foo="booyah")

    def updated_data(self):
        return dict(
            title="Cramer 2: Electric Booyah-loo",
            foo="whatta guy....booyah indeed!",
            authors=[{
                         "id": self.author.id,
                         "username": self.author.username,
                         "email": "",
                         "full_name": "Chris Sinchok",
                         "short_name": "Chris",
                         "first_name": "Chris",
                         "last_name": "Sinchok"
                     }]
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
        # self.content.tags.add(self.tags[0])

    def updated_data(self):
        # avoid the app register hell - serializers need to get user model
        from bulbs.content.serializers import TagSerializer

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


class TestImageAPI(BaseAPITestCase):
    def test_image_serializer(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content(
            TestContentDetailImage,
            detail_image=None
        )
        content_detail_url = reverse("content-detail", kwargs={"pk": content.id})

        response = client.get(content_detail_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["thumbnail"], None)
        self.assertEqual(data["detail_image"], None)


        # self.assertTrue("caption" in data["detail_image"])


class TestMeApi(BaseAPITestCase):
    def test_me(self):
        client = Client()
        client.login(username="admin", password="secret")
        me_endpoint = reverse("me")

        response = client.get(me_endpoint, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), "admin")

    def test_me_has_firebase_token(self):
        """Test that firebase token is put into me view if settings contains a FIREBASE_SECRET variable."""

        # login user
        client = Client()
        client.login(username="admin", password="secret")
        me_endpoint = reverse("me")

        # set the firebase secret needed to get the firebase_token property in the me view
        from django.conf import settings as mock_settings

        mock_settings.FIREBASE_SECRET = 'abc'

        # check that me view has the firebase token
        response = client.get(me_endpoint, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("firebase_token" in response.data)

    def test_me_as_superuser(self):
        """Test that super users get an addtional is_superuser property and regular users do not."""

        User = get_user_model()
        # login and test regular user
        client = Client()
        User.objects.create_user("regularuser", "regularguy@aol.com", "passward")
        client.login(username="regularuser", password="passward")
        response = client.get(reverse("me"), content_type="application/json")

        self.assertTrue("is_superuser" not in response.data)

        # login and test a superuser
        User.objects.create_superuser("superuser", "su@theonion.com", "password")
        client.login(username="superuser", password="password")
        response = client.get(reverse("me"), content_type="application/json")

        self.assertTrue(response.data["is_superuser"])


class TestTrashContentAPI(BaseAPITestCase):
    def test_trash(self):
        content = make_content()
        self.assertTrue(content.indexed)
        data = self.es.get(index=content.get_index_name(), doc_type=content.get_mapping_type_name(),
                           id=content.id)
        self.assertEqual(data["_source"]["title"], content.title)

        client = Client()
        client.login(username="admin", password="secret")
        content_rest_url = reverse("content-trash", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        # not just anyone can trash an article
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # now you can trash
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = Content.objects.get(id=content.id)
        self.assertFalse(content.indexed)

        # check for a log
        LogEntry.objects.filter(object_id=content.pk).get(change_message="Trashed")

        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            self.es.get(index=content.get_index_name(), doc_type=content.get_mapping_type_name(),
                        id=content.id)

        content.save()
        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            self.es.get(index=content.get_index_name(), doc_type=content.get_mapping_type_name(),
                        id=content.id)

    def test_trash_404(self):
        client = Client()
        client.login(username="admin", password="secret")
        content = make_content()
        content_rest_url = reverse("content-trash", kwargs={"pk": content.id})
        response = client.post(content_rest_url, content_type="application/json")
        # no permissions, no trashing
        self.assertEqual(response.status_code, 403)
        self.give_permissions()
        # now you can trash
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response = client.post(content_rest_url, content_type="application/json")
        self.assertEqual(response.status_code, 404)


class TestTokenAPI(BaseAPITestCase):
    def setUp(self):
        super(TestTokenAPI, self).setUp()

        self.client = Client()
        self.client.login(username="admin", password="secret")

    def test_create_token(self):
        """Test token creation."""

        # create a test piece of content
        content = Content.objects.create()

        # do request
        create_date = datetime.now()
        expire_date = create_date + timedelta(days=3)
        response = self.client.post(
            reverse("content-create-token", kwargs={"pk": content.id}),
            json.dumps({
                "create_date": create_date.isoformat(),
                "expire_date": expire_date.isoformat()
            }),
            content_type="application/json"
        )

        # test that what we expect to happen happened
        json_response = json.loads(response.content)
        self.assertEquals(len(json_response["url_uuid"]), 32)
        self.assertEquals(json_response["content"], 1)
        self.assertEquals(ObfuscatedUrlInfo.objects.count(), 1)
        self.assertEquals(ObfuscatedUrlInfo.objects.all()[0].content.id, 1)

    def test_list_tokens(self):
        """Test token listing."""

        # create some test content
        content = make_content()
        content_2 = make_content()
        create_date = datetime.now()
        expire_date = create_date + timedelta(days=3)
        info_1 = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat())
        info_2 = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat())
        info_3 = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat())
        ObfuscatedUrlInfo.objects.create(
            content=content_2,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat())

        # attempt to get tokens
        response = self.client.get(reverse("content-list-tokens", kwargs={"pk": content.id}))

        # check out stuff
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 3)
        self.assertEqual(json_response[0]["id"], info_1.id)
        self.assertEqual(json_response[0]["url_uuid"], info_1.url_uuid)
        self.assertEqual(json_response[1]["id"], info_2.id)
        self.assertEqual(json_response[2]["id"], info_3.id)
