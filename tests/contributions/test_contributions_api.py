import json

from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.contributions.models import Contribution, ContributorRole
from bulbs.utils.test import  BaseAPITestCase, make_content


class ContributionApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionApiTestCase, self).setUp()
        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor"),
            "writer": ContributorRole.objects.create(name="Writer")
        }

    def test_contributionrole_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        endpoint = reverse("contributorrole-list", )
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_contributions_list_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()

        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        Contribution.objects.create(
            content=content,
            contributor=self.admin,
            role=self.roles["editor"]
        )

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    # def test_contributions_list_api(self):
    # client = Client()
    #     client.login(username="admin", password="secret")
    #     content = TestContentObj.objects.create(title="I'm just an article")
    #     endpoint = reverse("content-contributions", kwargs={"pk": content.pk})
    #     response = client.get(endpoint, params={"pk": content.pk})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 0)
    #     Contribution.objects.create(
    #         content=content,
    #         contributor=self.admin,
    #         role=self.roles["editor"]
    #     )
    #     response = client.get(endpoint)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 1)

    def test_contributions_create_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()
        self.assertEqual(Contribution.objects.filter(content=content).count(), 0)
        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        data = [{
            "contributor": {
                "username": self.admin.username,
                "id": self.admin.id
                },
            "content": content.id
        }]
        response = client.post(endpoint, json.dumps(data), content_type="application/json")
        print(response.content)
        self.assertEqual(response.status_code, 400)

        self.assertEqual(Contribution.objects.filter(content=content).count(), 0)

        data = [{
            "contributor": {
                "username": self.admin.username,
                "id": self.admin.id
                },
            "role": self.roles["writer"].id,
            "content": content.id
        }]
        response = client.post(endpoint, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Contribution.objects.filter(content=content).count(), 1)
