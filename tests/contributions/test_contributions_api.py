import json

from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import Content, FeatureType
from bulbs.contributions.models import (Contribution, ContributorRole, ContributionRate, 
    ContributorRoleRate, FeatureTypeRate, Rate, RATE_PAYMENT_TYPES)
from bulbs.contributions.serializers import RateSerializer
from bulbs.utils.test import BaseAPITestCase, make_content


PAYMENT_TYPES = dict((label, value) for value, label in RATE_PAYMENT_TYPES)


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

    def test_rate_serialization(self):
        content = make_content()
        editor = self.roles['editor']
        contribution = Contribution.objects.create(
            content=content,
            contributor=self.admin,
            role=editor
        )
        feature = FeatureType.objects.create(name='MyFavorite')
        content.feature_type = feature
        content.save()

        regular_rate = Rate.objects.create(name=PAYMENT_TYPES['Manual'], rate=1000)
        serializer_data = RateSerializer(regular_rate).data
        self.assertEqual(serializer_data['id'], regular_rate.id)
        self.assertEqual(serializer_data['rate'], 1000)
        self.assertEqual(serializer_data['name'], 'Manual')
        self.assertIsNotNone(serializer_data['updated_on'])

        flat_rate = ContributorRoleRate.objects.create(name=PAYMENT_TYPES['Flat Rate'], rate=555, role=editor)        
        serializer_data = RateSerializer(flat_rate).data
        self.assertEqual(serializer_data['id'], flat_rate.id)
        self.assertEqual(serializer_data['rate'], 555)
        self.assertEqual(serializer_data['name'], 'Flat Rate')
        self.assertIsNotNone(serializer_data['updated_on'])

        hourly_rate = ContributorRoleRate.objects.create(name=PAYMENT_TYPES['Hourly'], rate=557, role=editor)
        serializer_data = RateSerializer(hourly_rate).data
        self.assertEqual(serializer_data['id'], hourly_rate.id)
        self.assertEqual(serializer_data['rate'], 557)
        self.assertEqual(serializer_data['name'], 'Hourly')
        self.assertIsNotNone(serializer_data['updated_on'])

        manual_rate = ContributionRate.objects.create(
            name=PAYMENT_TYPES['Manual'], rate=666, contribution=contribution)
        serializer_data = RateSerializer(manual_rate).data
        self.assertEqual(serializer_data['id'], manual_rate.id)
        self.assertEqual(serializer_data['rate'], 666)
        self.assertEqual(serializer_data['name'], 'Manual')
        self.assertIsNotNone(serializer_data['updated_on'])

        override_rate = ContributionRate.objects.create(
            name=PAYMENT_TYPES['Override'], rate=777, contribution=contribution)
        serializer_data = RateSerializer(override_rate).data
        self.assertEqual(serializer_data['id'], override_rate.id)
        self.assertEqual(serializer_data['rate'], 777)
        self.assertEqual(serializer_data['name'], 'Override')
        self.assertIsNotNone(serializer_data['updated_on'])

        feature_rate = FeatureTypeRate.objects.create(
            feature_type=feature, name=PAYMENT_TYPES['FeatureType'], rate=888)
        serializer_data = RateSerializer(feature_rate).data
        self.assertEqual(serializer_data['id'], feature_rate.id)
        self.assertEqual(serializer_data['rate'], 888)
        self.assertEqual(serializer_data['name'], 'FeatureType')
        self.assertIsNotNone(serializer_data['updated_on'])

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
        flat = ContributorRoleRate.objects.create(name=PAYMENT_TYPES['Flat Rate'], rate=1, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertIsNone(rate)

        # Add a Manual rate
        manual = ContributionRate.objects.create(name=PAYMENT_TYPES['Manual'], rate=2, contribution=contribution)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': manual.id, 'rate': 2, 'name': 'Manual'})

        # change to Flat Rate
        editor.payment_type = PAYMENT_TYPES['Flat Rate']
        editor.save()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': flat.id, 'rate': 1, 'name': 'Flat Rate'})

        # change to FeatureType
        feature = FeatureType.objects.create(name='A Fun Feature For Kids!')
        content.feature_type = feature
        content.save()
        feature_rate = FeatureTypeRate.objects.create(name=PAYMENT_TYPES['FeatureType'], feature_type=feature, rate=50)

        editor.payment_type = PAYMENT_TYPES['FeatureType']
        editor.save()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': feature_rate.id, 'rate': 50, 'name': 'FeatureType'})

        # change to Hourly
        editor.payment_type = PAYMENT_TYPES['Hourly']
        editor.save()
        hourly = ContributorRoleRate.objects.create(
            name=PAYMENT_TYPES['Hourly'], rate=66, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': hourly.id, 'rate': 66, 'name': 'Hourly'})


        # Override the rate
        override = ContributionRate.objects.create(
            name=PAYMENT_TYPES['Override'], rate=1000, contribution=contribution)

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
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
