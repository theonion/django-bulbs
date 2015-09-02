import json

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import Content, FeatureType
from bulbs.contributions.models import (Contribution, ContributorRole, ManualRate, HourlyRate, FlatRate, FeatureTypeOverride, FeatureTypeRate, LineItem, Override, Rate, RATE_PAYMENT_TYPES)
from bulbs.contributions.serializers import RateSerializer
from bulbs.utils.test import BaseAPITestCase, make_content


PAYMENT_TYPES = dict((label, value) for value, label in RATE_PAYMENT_TYPES)


class ContributionApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionApiTestCase, self).setUp()
        Contributor = get_user_model()
        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor"),
            "writer": ContributorRole.objects.create(name="Writer")
        }

        self.contributors = {
            "jarvis": Contributor.objects.create(
                first_name="jarvis",
                last_name="monster",
                username="arduous"
            ),
            "marvin": Contributor.objects.create(
                first_name="marvin",
                last_name="complete",
                username="argyle"
            ),
        }

    def test_contributionrole_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        endpoint = reverse("contributorrole-list")
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        payment_type = response.data[0].get('payment_type', None)
        self.assertEqual(payment_type, 'Manual')
        rates = response.data[0].get('rates')
        self.assertEqual(rates, dict())

        # Add some rates
        editor = self.roles.get("editor")
        editor_rate = FlatRate.objects.create(name=0, rate=100, role=editor)
        self.assertIsNotNone(editor_rate.updated_on)

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)

        rates = response.data[0].get('rates')
        self.assertEqual(rates["flat_rate"]['rate'], 100)
        self.assertIsNotNone(rates["flat_rate"]['updated_on'])

    def test_contributionrole_flat_rate_dict(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("contributorrole-list")
        data = {
            "name": "Big Fella",
            "payment_type": "FeatureType",
            "rates": {
                "flat_rate": {"rate": 50}
            }
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

    def test_update_payment_types(self):
        client = Client()
        client.login(username="admin", password="secret")

        endpoint = reverse("contributorrole-list")
        data = {
            "name": "the best fella",
            "payment_type": "Flat Rate"
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        data.update(resp.data)
        detail_endpoint = reverse("contributorrole-detail", kwargs={"pk": resp.data.get("id")})

        # Confirm flat rate returns
        resp = client.get(detail_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "Flat Rate")

        # Update to FeatureType
        data["payment_type"] = "FeatureType"
        resp = client.put(
            detail_endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "FeatureType")
        resp = client.get(detail_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "FeatureType")
        data.update(resp.data)

        # Update to Hourly
        data["payment_type"] = "Hourly"
        resp = client.put(
            detail_endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "Hourly")
        resp = client.get(detail_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "Hourly")
        data.update(resp.data)

        # Update to Manual
        data["payment_type"] = "Manual"
        resp = client.put(
            detail_endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "Manual")
        resp = client.get(detail_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get("payment_type"), "Manual")
        data.update(resp.data)

    def test_post_contributionrole_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("contributorrole-list")
        data = {
            "name": "Author",
            "description": "good guy stuff",
            "payment_type": "Flat Rate",
            "rates": {
                "flat_rate": {
                  "updated_on": "2015-07-13T20:14:48.573940Z",
                  "rate": 100
                },
                'hourly': {
                  "updated_on": '2015-07-14T20:14:48.573940Z',
                  "rate": 60
                },
                'feature_type': [{
                        "feature_type": '100 Episodes',
                        "updated_on": '2015-07-14T20:14:48.573940Z',
                        "rate": 100
                    }, {
                        "feature_type": '11 Question',
                        "updated_on": '2015-07-14T20:14:48.573940Z',
                        "rate": 11
                    }, {
                        "feature_type": '13 Days of Christmas',
                        "updated_on": '2015-07-14T20:14:48.573940Z',
                        "rate": 13
                    }, {
                        "feature_type": '15 Minutes or Less',
                        "updated_on": '2015-07-14T20:14:48.573940Z',
                        "rate": 15
                    }, {
                        "feature_type": '24 Hours Of',
                        "updated_on": '2015-07-14T20:14:48.573940Z',
                        "rate": 5
                }]
            }
        }

        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

        id = resp.data.get("id", None)
        self.assertIsNotNone(id)
        self.assertEqual(resp.data.get("payment_type"), "Flat Rate")

        role = ContributorRole.objects.get(id=int(id))
        self.assertEqual(role.name, data["name"])
        self.assertEqual(role.description, data["description"])
        self.assertEqual(role.payment_type, 0)

        # Make a PUT request
        endpoint = reverse("contributorrole-detail", kwargs={"pk": role.id})
        data["rates"]["flat_rate"]["rate"] = 120
        data["rates"]["hourly"]["rate"] = 100
        data["rates"]["feature_type"][0]["rate"] = 300
        resp = client.put(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["rates"]["flat_rate"]["rate"], 120)
        self.assertEqual(resp.data["rates"]["hourly"]["rate"], 100)
        self.assertEqual(resp.data["rates"]["feature_type"][0]["rate"], 300)

        # Test Hourlyr
        endpoint = reverse("contributorrole-list")
        data = {
            "name": "Good Fella",
            "payment_type": "Hourly"
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )

    def test_line_item_list_api(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("line-items-list")
        LineItem.objects.create(
            contributor=self.contributors["jarvis"],
            amount=50,
            note="eyyy good lookin out",
            payment_date=timezone.now() - timezone.timedelta(days=1)
        )
        LineItem.objects.create(
            contributor=self.contributors["marvin"],
            amount=60,
            note="c'mon buster",
            payment_date=timezone.now() - timezone.timedelta(days=3)
        )
        resp = client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_line_item_post_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("line-items-list")
        data = {
            "contributor": {
                "id": self.contributors["jarvis"].id
            },
            "amount": 66,
            "note": "eyyyyy",
            "payment_date": "2015-08-27T15:36:52.574182Z"
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

        # Make a PUT request
        endpoint = reverse("line-items-detail", kwargs={"pk": resp.data.get("id")})
        data.update(resp.data)
        data["payment_date"] = "2015-09-28T16:56:56.266Z"
        data["amount"] = 77
        resp = client.put(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)

    def test_rate_overrides_list_api(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("rate-overrides-list")
        override1 = Override.objects.create(
            rate=60,
            role=self.roles["editor"],
            contributor=self.contributors["jarvis"]
        )
        override2 = Override.objects.create(
            rate=50,
            role=self.roles["writer"],
            contributor=self.contributors["marvin"]
        )

        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

        overrides = sorted(resp.data, key=lambda override: override["id"])
        o1, o2 = overrides[0], overrides[1]
        o1c, o1r = o1.get("contributor"), o1.get("role")
        o2c, o2r = o2.get("contributor"), o2.get("role")
        self.assertEqual(o1.get("rate"), override1.rate)
        self.assertEqual(o1c.get("full_name"), "jarvis monster")
        self.assertEqual(o1r.get("name"), "Editor")
        self.assertEqual(o2.get("rate"), override2.rate)
        self.assertEqual(o2c.get("full_name"), "marvin complete")
        self.assertEqual(o2r.get("name"), "Writer")

    def test_rate_overrides_post_api_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("rate-overrides-list")
        data = {
            "rate": 70,
            "contributor": {
                "id": self.contributors["jarvis"].id
            },
            "role": {
                "id": self.roles["editor"].id
            }
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        override = Override.objects.get(id=resp.data.get("id"))
        self.assertEqual(resp.data.get("rate"), 70)
        self.assertEqual(resp.data.get("rate"), override.rate)
        self.assertEqual(resp.data.get("role").get("id"), override.role.id)
        self.assertEqual(
            resp.data.get("contributor").get("id"), override.contributor.id
        )

    def test_feature_type_override_list_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("rate-overrides-list")
        f1 = FeatureType.objects.create(name="ha ha!")
        f2 = FeatureType.objects.create(name="no no.")
        FeatureTypeOverride.objects.create(
            rate=55,
            feature_type=f1,
            role=self.roles["editor"],
            contributor=self.contributors["jarvis"]
        )
        FeatureTypeOverride.objects.create(
            rate=55,
            feature_type=f2,
            role=self.roles["writer"],
            contributor=self.contributors["marvin"]
        )
        resp = client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_feature_type_post_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("rate-overrides-list")
        f1 = FeatureType.objects.create(name="ha ha!")
        data = {
            "rate": 88,
            "contributor": {
                "id": self.contributors["jarvis"].id
            },
            "role": {
                "id": self.roles["editor"].id,
            },
            "feature_type": {
                "id": f1.id
            }
        }
        resp = client.post(
            endpoint,
            json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

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

        flat_rate = FlatRate.objects.create(name=PAYMENT_TYPES['Flat Rate'], rate=555, role=editor)
        serializer_data = RateSerializer(flat_rate).data
        self.assertEqual(serializer_data['id'], flat_rate.id)
        self.assertEqual(serializer_data['rate'], 555)
        self.assertEqual(serializer_data['name'], 'Flat Rate')
        self.assertIsNotNone(serializer_data['updated_on'])

        hourly_rate = FlatRate.objects.create(name=PAYMENT_TYPES['Hourly'], rate=557, role=editor)
        serializer_data = RateSerializer(hourly_rate).data
        self.assertEqual(serializer_data['id'], hourly_rate.id)
        self.assertEqual(serializer_data['rate'], 557)
        self.assertEqual(serializer_data['name'], 'Hourly')
        self.assertIsNotNone(serializer_data['updated_on'])

        manual_rate = ManualRate.objects.create(
            name=PAYMENT_TYPES['Manual'], rate=666, contribution=contribution)
        serializer_data = RateSerializer(manual_rate).data
        self.assertEqual(serializer_data['id'], manual_rate.id)
        self.assertEqual(serializer_data['rate'], 666)
        self.assertEqual(serializer_data['name'], 'Manual')
        self.assertIsNotNone(serializer_data['updated_on'])

        override_rate = ManualRate.objects.create(
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
        flat = FlatRate.objects.create(name=PAYMENT_TYPES['Flat Rate'], rate=1, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        self.assertIsNone(rate)

        # Add a Manual rate
        manual = ManualRate.objects.create(name=PAYMENT_TYPES['Manual'], rate=2, contribution=contribution)
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
        hourly = HourlyRate.objects.create(
            name=PAYMENT_TYPES['Hourly'], rate=66, role=editor)
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': hourly.id, 'rate': 66, 'name': 'Hourly'})

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

    def test_contribution_post_rate(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()
        Content.objects.get(id=content.id)
        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        rate_data =  "667"
        contributor_data = {
            "username": self.admin.username,
            "id": self.admin.id
        }
        contribution_data = [{
            "rate": rate_data,
            "contributor": contributor_data,
            "content": content.id,
            "force_payment": True,
            "role": self.roles["editor"].id
        }]

        response = client.post(
            endpoint, json.dumps(contribution_data), content_type="application/json")
        contribution = response.data[0]
        contributor = contribution.get('contributor')
        rate = contribution.get('rate')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(contributor['username'], 'admin')
        self.assertEqual(contributor['id'], self.admin.id)
        self.assertEqual(rate['rate'], 667)
        self.assertEqual(rate['name'], 'Manual')
        self.assertEqual(contribution['content'], content.id),
        self.assertEqual(contribution["force_payment"], True)
        self.assertEqual(contribution['role']['id'], 1)

    def test_contribution_post_override_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        content = make_content()
        Content.objects.get(id=content.id)
        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        rate_data = {
            'name': 'Flat Rate',
            'rate': 667
        }
        contributor_data = {
            "username": self.admin.username,
            "id": self.admin.id
        }
        contribution_data = [{
            "rate": rate_data,
            "override_rate": 70,
            "contributor": contributor_data,
            "content": content.id,
            "role": self.roles["editor"].id
        }]

        response = client.post(
            endpoint, json.dumps(contribution_data), content_type="application/json")
        override_rate = response.data[0].get("override_rate")
        self.assertEqual(override_rate, 70)

        response = client.get(endpoint)
        override_rate = response.data[0].get("override_rate")
        self.assertEqual(override_rate, 70)

        # Update the rate
        contribution_data[0]["override_rate"] = 100
        response = client.post(
            endpoint,
            json.dumps(contribution_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        override_rate = response.data[0].get("override_rate")
        self.assertEqual(override_rate, 100)


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
