import datetime
import json

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone

from bulbs.promotion.models import PZone, PZoneHistory
from bulbs.promotion.operations import PZoneOperation, InsertOperation, DeleteOperation
from bulbs.utils.test import  BaseAPITestCase, make_content


class PromotionApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(PromotionApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

        # set up a test pzone
        self.pzone = PZone.objects.create(name="homepage")
        data = []
        for i in range(10):
            content = make_content(title="Content test #{}".format(i))
            data.append({"id": content.pk})

        self.pzone.data = data
        self.pzone.save()

    def test_pzone_api(self):

        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        response = self.client.get(endpoint)
        # give permissions
        self.give_permissions()
        response = self.client.get(endpoint)
        # permission allows promotion
        self.assertEqual(response.status_code, 200)

        for index, content in enumerate(response.data["content"]):
            self.assertEqual(content["title"], "Content test #{}".format(index))

        new_data = response.data
        # This sucks, but it just reverses the list
        new_data["content"] = [{"id": content["id"]} for content in response.data["content"]][::-1]

        self.assertEqual(PZoneHistory.objects.count(), 0)

        response = self.client.put(endpoint, json.dumps(new_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        for index, content in enumerate(response.data["content"]):
            self.assertEqual(content["title"], "Content test #{}".format(9 - index))

        self.assertEqual(PZoneHistory.objects.count(), 1)
        pzone = PZone.objects.get(name=self.pzone.name)
        self.assertEqual(PZoneHistory.objects.get().data, pzone.data)

    def test_operations_permissions(self):
        """Ensure permissions limit who can edit operations."""

        # create regular user
        regular_user_name = "regularuser"
        regular_user_pass = "12345"
        get_user_model().objects.create_user(
            regular_user_name,
            "regularguy@aol.com",
            regular_user_pass
        )
        self.client.login(username=regular_user_name, password=regular_user_pass)

        # do requests
        response_get = self.client.get(reverse(
            "pzone_operations",
            kwargs={
                "pzone_pk": self.pzone.pk
            }
        ))
        response_post = self.client.post(reverse(
            "pzone_operations",
            kwargs={
                "pzone_pk": self.pzone.pk
            }
        ))
        response_delete = self.client.delete(reverse(
            "pzone_operations_delete",
            kwargs={
                "pzone_pk": self.pzone.pk,
                "operation_pk": 1
            }
        ))

        # check that we get 403 for everything
        self.assertEqual(response_get.status_code, 403)
        self.assertEqual(response_post.status_code, 403)
        self.assertEqual(response_delete.status_code, 403)

    def test_get_operations(self):
        """Test that we can get a pzone's operations."""

        # set up some test operations
        test_time = (timezone.now() + datetime.timedelta(hours=-1)).replace(microsecond=0)
        new_content_1 = make_content()
        op_1 = InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content_1
        )
        op_1_type = "{}_{}".format(op_1.polymorphic_ctype.app_label, op_1.polymorphic_ctype.model)
        # this one should end up above the first one
        new_content_2 = make_content()
        op_2 = InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content_2
        )
        op_2_type = "{}_{}".format(op_2.polymorphic_ctype.app_label, op_2.polymorphic_ctype.model)

        # query the endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": self.pzone.pk
        })
        response = self.client.get(endpoint)

        # check that we got an OK response
        self.assertEqual(response.status_code, 200, msg=response.data)

        # start checking data
        operations = response.data
        self.assertEqual(len(operations), 2)

        # check first operation made it in
        self.assertEqual(operations[0]["type_name"], op_1_type)
        self.assertEqual(operations[0]["content"], new_content_1.pk)
        self.assertEqual(operations[0]["pzone"], self.pzone.pk)
        self.assertEqual(operations[0]["index"], 0)
        self.assertEqual(operations[0]["content_title"], new_content_1.title)
        self.assertEqual(operations[0]["when"], test_time.isoformat().replace("+00:00", "Z"))
        # check second operation made it in
        self.assertEqual(operations[1]["type_name"], op_2_type)
        self.assertEqual(operations[1]["content"], new_content_2.pk)
        self.assertEqual(operations[1]["pzone"], self.pzone.pk)
        self.assertEqual(operations[1]["index"], 0)
        self.assertEqual(operations[1]["content_title"], new_content_2.title)
        self.assertEqual(operations[1]["when"], test_time.isoformat().replace("+00:00", "Z"))

    def test_get_operations_404(self):
        """Test that a 404 is thrown when an id not associated with a pzone
        is given."""

        # query endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": 1234
        })
        response = self.client.get(endpoint)

        # check that we got a 404
        self.assertEqual(response.status_code, 404)

    def test_get_operations_empty(self):
        """Test that the response of an empty operations list is JSON."""

        # query the endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": self.pzone.pk
        })
        response = self.client.get(endpoint)

        # check that we got an OK response
        self.assertEqual(response.status_code, 200, msg=response.data)

        # start checking data
        operations = response.data
        self.assertEqual(len(operations), 0)

    def test_post_operations(self):
        """Test that a new operation can be added to a pzone operations."""

        # test objects
        test_time = (timezone.now() + datetime.timedelta(hours=1)).replace(microsecond=0)

        test_content_1 = make_content(published=timezone.now())
        test_content_2 = make_content(published=timezone.now())

        # setup and query endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": self.pzone.pk
        })
        response = self.client.post(
            endpoint,
            json.dumps([
                {
                    "type_name": "promotion_replaceoperation",
                    "pzone": self.pzone.pk,
                    "when": test_time.isoformat(),
                    "index": 1,
                    "content": test_content_1.id
                },
                {
                    "type_name": "promotion_replaceoperation",
                    "pzone": self.pzone.pk,
                    "when": test_time.isoformat(),
                    "index": 2,
                    "content": test_content_2.id
                },
            ]),
            content_type="application/json"
        )

        # check that we got an OK response
        self.assertEqual(response.status_code, 200, msg=response.data)

        # check that operations made it into the db
        self.assertEqual(PZoneOperation.objects.count(), 2)

        # check response data data
        operations = response.data
        self.assertNotEqual(operations[0]["id"], None)
        self.assertEqual(operations[0]["type_name"], "promotion_replaceoperation")
        self.assertEqual(operations[0]["pzone"], self.pzone.pk)
        self.assertEqual(operations[0]["when"], test_time.isoformat().replace("+00:00", "Z"))
        self.assertEqual(operations[0]["index"], 1)
        self.assertEqual(operations[0]["content"], test_content_1.id)

        assert operations[1]["id"] > operations[0]["id"]
        self.assertEqual(operations[1]["type_name"], "promotion_replaceoperation")
        self.assertEqual(operations[1]["pzone"], self.pzone.pk)
        self.assertEqual(operations[1]["when"], test_time.isoformat().replace("+00:00", "Z"))
        self.assertEqual(operations[1]["index"], 2)
        self.assertEqual(operations[1]["content"], test_content_2.id)

    def test_post_operation(self):
        """Test that a new operation can be added to a pzone operations."""

        # test objects
        test_time = (timezone.now() + datetime.timedelta(hours=1)).replace(microsecond=0)

        # setup and query endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": self.pzone.pk
        })
        response = self.client.post(
            endpoint,
            json.dumps({
                "type_name": "promotion_replaceoperation",
                "pzone": self.pzone.pk,
                "when": test_time.isoformat(),
                "index": 0,
                "content": 1
            }),
            content_type="application/json"
        )

        # check that we got an OK response
        self.assertEqual(response.status_code, 200, msg=response.data)

        # check that operations made it into the db
        self.assertEqual(PZoneOperation.objects.count(), 1)

        # check response data data
        operation = response.data
        self.assertNotEqual(operation["id"], None)
        self.assertEqual(operation["type_name"], "promotion_replaceoperation")
        self.assertEqual(operation["pzone"], self.pzone.pk)
        self.assertEqual(operation["when"], test_time.isoformat().replace("+00:00", "Z"))
        self.assertEqual(operation["index"], 0)
        self.assertEqual(operation["content"], 1)

    def test_post_operation_400(self):
        """Test that posting with bad data returns 400 and errors in json."""

        # setup and query endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": self.pzone.pk
        })
        response = self.client.post(
            endpoint,
            json.dumps({
                "type_name": "not a real operation type"
            }),
            content_type="application/json"
        )

        # check that we got a 400 response
        self.assertEqual(response.status_code, 400)
        # check the data that came back to see if it has an error
        self.assertEqual(len(response.data["errors"]), 1)

        # let's try another error
        response = self.client.post(
            endpoint,
            json.dumps({
                "type_name": "promotion_replaceoperation",
                "pzone": "123"
            }),
            content_type="application/json"
        )

        # check that we got a 400 response
        self.assertEqual(response.status_code, 400)
        # check that the data came back with 4 errors
        self.assertEqual(len(response.data), 4)

    def test_post_operation_404(self):
        """Test that posting with invalid pzone pk returns a 404."""

        # query endpoint
        endpoint = reverse("pzone_operations", kwargs={
            "pzone_pk": 123456789
        })
        response = self.client.post(endpoint)

        # check that we got a 400 response
        self.assertEqual(response.status_code, 404)

    def test_delete_operation(self):
        """Test that we can remove an operation from a pzone."""

        # add an operation to the db
        test_time = timezone.now() + datetime.timedelta(hours=1)
        new_content = make_content()
        new_operation = InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content
        )

        # setup and query endpoint
        endpoint = reverse("pzone_operations_delete", kwargs={
            "pzone_pk": self.pzone.pk,
            "operation_pk": new_operation.pk
        })
        response = self.client.delete(endpoint)

        # check that we got an No Content (204) response
        self.assertEqual(response.status_code, 204, msg=response.data)

        # start checking data
        self.assertEqual(InsertOperation.objects.count(), 0)

    def test_delete_operation_404(self):
        """Test that we get a 404 when providing wrong operation info."""

        # query endpoint
        endpoint = reverse("pzone_operations_delete", kwargs={
            "pzone_pk": 1234,
            "operation_pk": 1234
        })
        response = self.client.delete(endpoint)

        # check that we got a 404
        self.assertEqual(response.status_code, 404)

    def test_get_applied(self):
        """Test that we can get a pzone applied when requesting to pzone detail
        without a preview time."""

        # make some testing stuff
        test_time = timezone.now() + datetime.timedelta(hours=-1)
        content_1 = self.pzone[0]
        content_2 = self.pzone[1]
        DeleteOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=content_1
        )
        DeleteOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=content_2
        )

        # setup endpoint
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        self.give_permissions()
        response = self.client.get(endpoint)

        # get updated pzone
        self.pzone = PZone.objects.get(name=self.pzone.name)

        # check response status
        self.assertEqual(response.status_code, 200)
        # check that response list is correct
        self.assertEqual(len(response.data["content"]), 8)
        self.assertNotEqual(response.data["content"][0]["id"], content_1.id)
        self.assertNotEqual(response.data["content"][0]["id"], content_2.id)
        # check that in db list is correct
        self.assertEqual(len(self.pzone), 8)
        self.assertNotEqual(self.pzone[0].id, content_1.id)
        self.assertNotEqual(self.pzone[0].id, content_2.id)
        # ensure we created a history object and its data matches
        self.assertEqual(self.pzone.history.count(), 1)
        self.assertEqual(self.pzone.history.all()[0].data, self.pzone.data)

    def test_get_preview(self):
        """Test that we can get a pzone preview."""

        # make some testing stuff
        test_time = timezone.now() + datetime.timedelta(hours=1)
        DeleteOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=self.pzone[0]
        )
        DeleteOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=self.pzone[1]
        )

        # setup endpoint
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        self.give_permissions()
        response = self.client.get(endpoint, {"preview": test_time.isoformat()})

        # check response status
        self.assertEqual(response.status_code, 200)
        # ensure nothing was actually deleted
        self.assertEqual(len(self.pzone), 10)
        # check that the preview has items deleted
        self.assertEqual(len(response.data["content"]), 8)

    def test_get_preview_403(self):
        """Ensure that we cannot get a preview if we don't have permission."""

        # create regular user
        regular_user_name = "regularuser"
        regular_user_pass = "12345"
        get_user_model().objects.create_user(
            regular_user_name,
            "regularguy@aol.com",
            regular_user_pass
        )
        self.client.login(username=regular_user_name, password=regular_user_pass)

        # setup endpoint and request
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        response = self.client.get(endpoint, {"preview": "1234"})

        self.assertEqual(response.status_code, 403)

    def test_put_pzone(self):
        """Ensure that PUTing a pzone works."""

        # swap two entries
        old_0 = self.pzone[0]
        old_1 = self.pzone[1]
        self.pzone[0], self.pzone[1] = self.pzone[1], self.pzone[0]

        # setup endpoint
        self.give_permissions()
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        response = self.client.put(
            endpoint,
            data=json.dumps({"content": self.pzone.data, "name": "homepage"}),
            content_type="application/json"
        )

        # check status
        self.assertEqual(
            response.status_code, 200,
            msg="Failed ({}): {}".format(response.status_code, response.data))

        # check that the pzone has been modified
        self.pzone = PZone.objects.get(name=self.pzone.name)
        self.assertEqual(self.pzone[0].id, old_1.id)
        self.assertEqual(self.pzone[1].id, old_0.id)

        # try to empy out the pzone
        self.pzone.data = []
        response = self.client.put(
            endpoint,
            data=json.dumps({"content": self.pzone.data, "name": "homepage"}),
            content_type="application/json"
        )
        self.assertEqual(
            response.status_code, 200,
            msg="Failed ({}): {}".format(response.status_code, response.data))
        self.pzone = PZone.objects.get(name=self.pzone.name)
        self.assertEqual(len(self.pzone), 0)



    def test_put_pzone_403(self):
        """Ensure that PUTing to a pzone without permission gives a 403."""

        # create regular user
        regular_user_name = "regularuser"
        regular_user_pass = "12345"
        get_user_model().objects.create_user(
            regular_user_name,
            "regularguy@aol.com",
            regular_user_pass
        )
        self.client.login(username=regular_user_name, password=regular_user_pass)

        # setup endpoint and make request
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        response = self.client.put(endpoint)

        self.assertEqual(response.status_code, 403)

    def test_get_past_pzone(self):
        """Ensure retrieving a past pzone accesses pzone history."""

        # create history, then take timestamp to test again, this order is important for timing
        content_id = 5
        history = self.pzone.history.create(
            data=[{"id": content_id}]
        )
        test_time = timezone.now()

        # cache pzone
        from django.core.cache import cache
        cache.set('pzone-history-' + self.pzone.name, history)

        # retrieve data
        endpoint = reverse("pzone-detail", kwargs={"pk": self.pzone.pk})
        self.give_permissions()
        response = self.client.get(endpoint, {"preview": test_time.isoformat()})

        # check that history was used
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["content"]), 1)
        self.assertEqual(response.data["content"][0]["id"], content_id)

