import time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone
from bulbs.utils.test import BaseIndexableTestCase

from bulbs.content.models import FeatureType, ObfuscatedUrlInfo, Content
from example.testcontent.models import TestContentObj, TestContentObjTwo
from bulbs.utils.test import make_content


class TestContentViews(BaseIndexableTestCase):
    def setUp(self):
        super(TestContentViews, self).setUp()
        User = get_user_model()
        self.client = Client()

        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_unpublished_article(self):
        content = TestContentObj.objects.create(title="Testing Content")
        response = self.client.get(reverse("published", kwargs={"pk": content.id}))
        self.assertEqual(response.status_code, 302)

        # But this should work when we login
        self.client.login(username="admin", password="secret")
        response = self.client.get(reverse("published", kwargs={"pk": content.id}))
        self.assertEqual(response.status_code, 200)

    def published_article(self):
        content = make_content(published=timezone.now() - timedelta(hours=2))
        response = self.client.get(reverse("published", kwargs={"pk": content.id}))
        self.assertEqual(response.status_code, 200)

    def test_content_list_views(self):
        ft = FeatureType.objects.create(name="Feature", slug="feature")
        content = make_content(TestContentObj, feature_type=ft, published=timezone.now() - timedelta(hours=2))
        content_two = make_content(TestContentObjTwo, feature_type=ft, published=timezone.now() - timedelta(hours=2))
        Content.search_objects.refresh()
        # make sure we get all content with this list
        r = self.client.get(reverse("example.testcontent.views.test_all_content_list"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(2, len(r.context_data["content_list"]))
        # make sure we only get TestContentTwoObjs from this other list
        r = self.client.get(reverse("example.testcontent.views.test_content_two_list"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(1, len(r.context_data["content_list"]))
        item = r.context_data["content_list"][0]
        ctype = ContentType.objects.get_for_id(item.polymorphic_ctype_id)
        self.assertIs(ctype.model_class(), TestContentObjTwo)

    def test_base_content_detail_view_tokenized_url(self):
        """Test that we can get an article via a /unpublished/<token> style url."""

        # create test content and token
        create_date = timezone.now()
        expire_date = create_date + timedelta(days=3)
        content = make_content(TestContentObj, published=None)
        obfuscated_url_info = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )
        uuid = obfuscated_url_info.url_uuid

        time.sleep(1)
        Content.search_objects.refresh()

        # attempt to get article via token
        response = self.client.get(reverse("unpublished", kwargs={"token": uuid}))

        # check that everything went well and we got the content id back from the view
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["content"].id, content.id)

    def test_base_content_detail_view_tokenized_url_outside_date_window(self):
        """Test that dates work for /unpublished/<token> style urls."""

        # create test content and token
        create_date = timezone.now() + timedelta(days=3)
        expire_date = create_date + timedelta(days=3)
        content = make_content(published=None)
        obfuscated_url_info = ObfuscatedUrlInfo.objects.create(
            content=content,
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )
        uuid = obfuscated_url_info.url_uuid

        # attempt to get article via token
        response = self.client.get(reverse("unpublished", kwargs={"token": uuid}))

        # expect that we got a 404
        self.assertEqual(response.status_code, 404)

    def test_base_content_detail_view_tokenized_url_invalid(self):
        """Test that we get a 404 when token is invalid."""

        # create test content and token
        create_date = timezone.now()
        expire_date = create_date + timedelta(days=3)
        ObfuscatedUrlInfo.objects.create(
            content=make_content(),
            create_date=create_date.isoformat(),
            expire_date=expire_date.isoformat()
        )

        # use some invalid token
        response = self.client.get(reverse("unpublished", kwargs={"token": 123}))

        # expect that we got a 404
        self.assertEqual(response.status_code, 404)
