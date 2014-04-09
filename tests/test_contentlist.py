import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.promotion.models import ContentList, ContentListHistory

from tests.testcontent.models import TestContentObj


class ContentListTestCase(BaseIndexableTestCase):

    def test_content_list(self):
        content_list = ContentList.objects.create(name="homepage")
        data = []
        for i in range(10):
            content = TestContentObj.objects.create(
                title="Content test #{}".format(i),
            )
            data.append({"id": content.pk})

        content_list.data = data
        content_list.save()

        self.assertEqual(len(content_list.content), 10)
        for index, content in enumerate(content_list.content):
            self.assertEqual(content.title, "Content test #{}".format(index))

    def test_content_list_api(self):
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()
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
        content_list = ContentList.objects.get(id=content_list.id)
        self.assertEqual(ContentListHistory.objects.get().data, content_list.data)
