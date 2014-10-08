import json
import datetime
from django.core.urlresolvers import reverse

from django.test import Client
from elastimorphic.tests.base import BaseIndexableTestCase
from rest_framework import serializers
from tests.utils import JsonEncoder


class TestAPI(BaseIndexableTestCase):

    def setUp(self):
        super(TestAPI, self).setUp()

        # log in
        self.client = Client()
        self.client.login(username="admin", password="secret")

    def test_listing(self):
        """Test creating and retrieving a list of notifications from the DB via the API."""

        time_now = datetime.datetime.now()

        data_cms_notification = {
            "title": "We've Made an Update!",
            "body": "Some updates were made on the site. Enjoy them while they last.",
            "post_date": time_now.isoformat(),
            "notify_end_date": (time_now + datetime.timedelta(days=3)).isoformat(),
            "editable": False
        }

        # post new listing
        self.client.post(
            reverse("notifications"),
            json.dumps(data_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        # get new listing
        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, 200)

        resp_cms_notification = json.loads(response.content)

        self.assertEqual(len(resp_cms_notification), 1)
        self.assertTrue("id" in resp_cms_notification[0])
        self.assertEqual(data_cms_notification["title"], resp_cms_notification[0]["title"])

        # attempt an update of listing
        up_cms_notification = resp_cms_notification[0]
        up_cms_notification["title"] = "Updated title"
        self.client.put(
            reverse("notifications", kwargs={"pk": up_cms_notification["id"]}),
            json.dumps(up_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, 200)

        up_resp_cms_notification = json.loads(response.content)

        self.assertEqual(len(up_resp_cms_notification), 1)
        self.assertEqual(up_cms_notification["title"], up_resp_cms_notification[0]["title"])

    def test_validation(self):
        """Test serializer validation."""

        time_now = datetime.datetime.now()

        data_cms_notification = {
            "title": "Dates Are All Wrong",
            "post_date": (time_now + datetime.timedelta(days=3)).isoformat(),
            "notify_end_date": time_now.isoformat(),
            "editable": True
        }

        # post new listing
        response = self.client.post(
            reverse("notifications"),
            json.dumps(data_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        errors = json.loads(response.content)

        self.assertEquals(errors["non_field_errors"][0], "Post date must occur before promotion end date.")

        response = self.client.get(reverse("notifications"))

        self.assertEqual(len(json.loads(response.content)), 0)
