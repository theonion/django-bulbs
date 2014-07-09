import json

from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.promotion.models import ContentList, ContentListHistory

from tests.test_content_api import ContentAPITestCase
from tests.testcontent.models import TestContentObj


class PromotionApiTestCase(ContentAPITestCase):

    def test_content_list_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        content_list = ContentList.objects.create(name="homepage")
        data = []
        for i in range(10):
            content = TestContentObj.objects.create(
                title="Content test #{}".format(i),
            )
            data.append({"id": content.pk})

        content_list.data = data
        content_list.save()

        endpoint = reverse("contentlist-detail", kwargs={"pk": content_list.pk})
        response = client.get(endpoint)
        # no permission, no promotion
        self.assertEqual(response.status_code, 403)
        # ok, have some permissions
        self.give_permissions()
        response = client.get(endpoint)
        # permission allows promotion
        self.assertEqual(response.status_code, 200)

        for index, content in enumerate(response.data["content"]):
            self.assertEqual(content["title"], "Content test #{}".format(index))

        new_data = response.data
        #  This sucks, but it just reverses the list
        new_data["content"] = [{"id": content["id"]} for content in response.data["content"]][::-1]

        self.assertEqual(ContentListHistory.objects.count(), 0)

        response = client.put(endpoint, json.dumps(new_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        for index, content in enumerate(response.data["content"]):
            self.assertEqual(content["title"], "Content test #{}".format(9 - index))

        self.assertEqual(ContentListHistory.objects.count(), 1)
        content_list = ContentList.objects.get(name=content_list.name)
        self.assertEqual(ContentListHistory.objects.get().data, content_list.data)
