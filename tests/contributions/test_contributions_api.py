import json

from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import Content, FeatureType
from bulbs.contributions.models import (Contribution, ContributorRole, ContributionRate, 
    ContributorRoleRate, FeatureTypeRate, RATE_PAYMENT_TYPES)
from bulbs.utils.test import BaseAPITestCase, make_content


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

        payment_type = response.data[0].get('payment_type', None)
        self.assertEqual(payment_type, 'Manual')
        rates = response.data[0].get('rates')
        self.assertEqual(rates, list())

        # Add some rates
        editor = self.roles.get("editor")
        editor_rate = ContributorRoleRate.objects.create(name=0, rate=100, role=editor)
        self.assertIsNotNone(editor_rate.updated_on)

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)

        rates = response.data[0].get('rates')
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates[0]['id'], editor_rate.id)
        self.assertEqual(rates[0]['name'], 'Flat Rate')
        self.assertEqual(rates[0]['rate'], 100)
        self.assertIsNotNone(rates[0]['updated_on'])

    def test_contributions_list_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()
        Content.objects.get(id=content.id)

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
        self.assertIsNone(response.data[0].get('minutes_worked'))

    def test_get_contribution_rate(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()
        Content.objects.get(id=content.id)
        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        editor = self.roles["editor"]        
        contribution = Contribution.objects.create(            
            content=content,
            contributor=self.admin,
            role=editor
        )

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        rate = response.data[0].get('rate')
        self.assertIsNone(rate)
        
        # Add Flat Rate, should not return
        flat = ContributorRoleRate.objects.create(name='Flat Rate', rate=1, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertIsNone(rate)

        # Add a Manual rate
        manual = ContributionRate.objects.create(name='Manual', rate=2, contribution=contribution)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertEqual(rate, {'id': manual.id, 'rate': 2, 'name': 'Manual'})

        # change to Flat Rate
        editor.payment_type = 'Flat Rate'
        editor.save()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertEqual(rate, {'id': flat.id, 'rate': 1, 'name': 'Flat Rate'})

        feature = FeatureType.objects.create(name='A Fun Feature For Kids!')
        content.feature_type = feature
        content.save()
        feature_rate = FeatureTypeRate.objects.create(name='FeatureType', feature_type=feature, rate=50)

        editor.payment_type = 'FeatureType'
        editor.save()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertEqual(rate, {'id': feature_rate.id, 'rate': 50, 'name': 'FeatureType'})

        # change to Hourly
        editor.payment_type = 'Hourly'
        editor.save()
        hourly = ContributorRoleRate.objects.create(name='Hourly', rate=66, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertEqual(rate, {'id': hourly.id, 'rate': 66, 'name': 'Hourly'})

        # Override the rate
        override = ContributionRate.objects.create(
            name='Override', rate=1000, contribution=contribution)

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        rate = response.data[0].get('rate')
        self.assertEqual(rate, {'id': override.id, 'rate': 1000, 'name': 'Override'})


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
        Content.search_objects.refresh()
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
        print(response.content)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Contribution.objects.filter(content=content).count(), 1)
