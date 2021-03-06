import json
import datetime
from bulbs.cms_notifications.models import CmsNotification

from django.core.urlresolvers import reverse
from django.test import Client
from bulbs.utils.test import JsonEncoder, BaseIndexableTestCase
from django.contrib.auth import get_user_model


class TestAPI(BaseIndexableTestCase):

    def setUp(self):
        super(TestAPI, self).setUp()
        User = get_user_model()

        # create a superuser and regular user
        self.superuser_pass = "password"
        self.regular_user_pass = "abc123"
        self.superuser = User.objects.create_superuser("superuser", "superuser@theonion.com", self.superuser_pass)
        self.regular_user = User.objects.create_user("regularuser", "regularguy@aol.com", self.regular_user_pass)

        self.client = Client()

    def test_listing(self):
        """Test creating and retrieving a list of CMS notifications from the DB via the API."""

        self.client.login(username=self.superuser.username, password=self.superuser_pass)

        time_now = datetime.datetime.now()

        data_cms_notification = {
            "title": "We've Made an Update!",
            "body": "Some updates were made on the site. Enjoy them while they last.",
            "post_date": time_now.isoformat(),
            "notify_end_date": (time_now + datetime.timedelta(days=3)).isoformat()
        }

        # post new listing
        self.client.post(
            reverse("cms_notifications"),
            json.dumps(data_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        # get new listing
        response = self.client.get(reverse("cms_notifications"))
        self.assertEqual(response.status_code, 200)

        resp_cms_notification = json.loads(response.content.decode("utf8"))

        self.assertEqual(len(resp_cms_notification), 1)
        self.assertTrue("id" in resp_cms_notification[0])
        self.assertEqual(data_cms_notification["title"], resp_cms_notification[0]["title"])

        # attempt an update of listing
        up_cms_notification = resp_cms_notification[0]
        up_cms_notification["title"] = "Updated title"
        self.client.put(
            reverse("cms_notifications", kwargs={"pk": up_cms_notification["id"]}),
            json.dumps(up_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        response = self.client.get(reverse("cms_notifications"))
        self.assertEqual(response.status_code, 200)

        up_resp_cms_notification = json.loads(response.content.decode("utf8"))

        self.assertEqual(len(up_resp_cms_notification), 1)
        self.assertEqual(up_cms_notification["title"], up_resp_cms_notification[0]["title"])

    def test_delete(self):
        """Test DELETEing a record."""

        self.client.login(username=self.superuser.username, password=self.superuser_pass)

        time_now = datetime.datetime.now()

        data_cms_notification = {
            "title": "We've Made an Update!",
            "body": "Some updates were made on the site. Enjoy them while they last.",
            "post_date": time_now.isoformat(),
            "notify_end_date": (time_now + datetime.timedelta(days=3)).isoformat()
        }

        # post new listing
        self.client.post(
            reverse("cms_notifications"),
            json.dumps(data_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(CmsNotification.objects.count(), 1)

        # delete listing
        delete_response = self.client.delete(reverse("cms_notifications",
                                                     kwargs={"pk": CmsNotification.objects.all()[0].id}))

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(CmsNotification.objects.count(), 0)

    def test_validation(self):
        """Test serializer validation."""

        self.client.login(username=self.superuser.username, password=self.superuser_pass)

        time_now = datetime.datetime.now()

        data_cms_notification = {
            "title": "Dates Are All Wrong",
            "post_date": (time_now + datetime.timedelta(days=3)).isoformat(),
            "notify_end_date": time_now.isoformat()
        }

        # post new listing
        response = self.client.post(
            reverse("cms_notifications"),
            json.dumps(data_cms_notification, cls=JsonEncoder),
            content_type="application/json"
        )

        errors = json.loads(response.content.decode("utf8"))

        self.assertEquals(errors["non_field_errors"][0], "Post date must occur before promotion end date.")

        response = self.client.get(reverse("cms_notifications"))

        self.assertEqual(len(json.loads(response.content.decode("utf8"))), 0)

    def test_permissions(self):
        """Test that only super users can PUT/POST."""

        # test a regular user first
        self.client.login(username=self.regular_user.username, password=self.regular_user_pass)

        post_response = self.client.post(reverse("cms_notifications"))
        put_response = self.client.put(reverse("cms_notifications"))
        get_response = self.client.get(reverse("cms_notifications"))
        delete_response = self.client.delete(reverse("cms_notifications"))

        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(put_response.status_code, 403)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 403)

        # now test a superuser
        self.client.login(username=self.superuser.username, password=self.superuser_pass)

        time_now = datetime.datetime.now()

        json_data = json.dumps({
            "title": "Dates Are All Wrong",
            "post_date": time_now.isoformat(),
            "notify_end_date": (time_now + datetime.timedelta(days=3)).isoformat()
        }, cls=JsonEncoder)

        post_response = self.client.post(reverse("cms_notifications"),
                                         json_data,
                                         content_type="application/json")
        notification_id = post_response.data["id"]
        put_response = self.client.put(reverse("cms_notifications", kwargs={"pk": notification_id}),
                                       json_data,
                                       content_type="application/json")
        get_response = self.client.get(reverse("cms_notifications"))
        delete_response = self.client.delete(reverse("cms_notifications", kwargs={"pk": notification_id}))

        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 204)
