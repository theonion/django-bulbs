import json

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import Content, FeatureType, Tag
from bulbs.contributions.models import (
    Contribution, ContributorRole, ManualRate, HourlyRate,
    FlatRate, FeatureTypeOverride, FeatureTypeRate, FreelanceProfile, LineItem, Override,
    Rate, RATE_PAYMENT_TYPES
)
from bulbs.contributions.serializers import RateSerializer
from bulbs.utils.test import BaseAPITestCase, make_content


PAYMENT_TYPES = dict((label, value) for value, label in RATE_PAYMENT_TYPES)


class ContributionApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionApiTestCase, self).setUp()
        Contributor = get_user_model()
        self.feature_types = {
            "surfing": FeatureType.objects.create(name="Surfing")
        }

        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor"),
            "writer": ContributorRole.objects.create(name="Writer", payment_type=0),
            "featured": ContributorRole.objects.create(name="Featured", payment_type=1),
            "friend": ContributorRole.objects.create(name="Friend", payment_type=3)
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
        self.assertEqual(len(response.data), 4)

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

    def test_contributor_role_overridable(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse('contributorrole-list')
        resp = client.get(endpoint + '?override=true')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_contributionrole_flat_rate_dict(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("contributorrole-list")
        data = {
            "name": "Big Fella",
            "payment_type": "FeatureType",
            "role": self.roles['featured'].id,
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
            },
            "feature_types": [
                {
                    "feature_type": "TV Club",
                    "rate": 1000
                }
            ]
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

    def test_override_feature_types(self):
        endpoint = reverse('rate-overrides-list')
        client = Client()
        client.login(username='admin', password='secret')
        data = {
            'contributor': {
                'username': self.contributors['jarvis'].username,
                'id': self.contributors['jarvis'].id,
            },
            'role': self.roles['featured'].id,
            'feature_types': [{'rate': 80, 'feature_type': self.feature_types["surfing"].name}]
        }
        resp = client.post(endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        id = resp.data.get('id')
        detail_endpoint = reverse('rate-overrides-detail', kwargs={'pk': id})
        data.update(resp.data)
        data['feature_types'][0]['rate'] = 100

        resp = client.put(detail_endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        feature_types = resp.data['feature_types']
        self.assertEqual(len(feature_types), 1)
        self.assertEqual(feature_types[0]['rate'], 100)

    # TODO: custom validation if no feature_types for rates

    def test_override_delete_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        override = Override.objects.create(
            rate=100,
            contributor=self.contributors["jarvis"],
            role=self.roles["editor"]
        )

        endpoint = reverse("rate-overrides-detail", kwargs={"pk": override.id})
        resp = client.get(endpoint)
        self.assertEqual(resp.status_code, 200)

        resp = client.delete(endpoint)
        self.assertEqual(resp.status_code, 204)

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
        manual = ManualRate.objects.create(
            name=PAYMENT_TYPES['Manual'],
            rate=2,
            contribution=contribution
        )
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
        FlatRate.objects.create(role=self.roles['writer'], rate=100)
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contribution.objects.filter(content=content).count(), 1)

    def test_rolefield_rate_interpretation(self):
        client = Client()
        client.login(username="admin", password="secret")
        feature_type = FeatureType.objects.create(name="Cams Favorite Stuff")
        feature_type_2 = FeatureType.objects.create(name="Bad Stuff")
        content = make_content(feature_type=feature_type)
        content_endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        # FlatRate contribution
        role = ContributorRole.objects.create(name="FlatRatePerson", payment_type=0)
        FlatRate.objects.create(role=role, rate=700)
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 700)
        contribution.delete()

        # FeatureType contribution
        role = ContributorRole.objects.create(name="FeatureTypePerson", payment_type=1)
        FeatureTypeRate.objects.create(
            role=role,
            feature_type=feature_type,
            rate=666
        )
        FeatureTypeRate.objects.create(
            role=role,
            feature_type=feature_type_2,
            rate=444
        )
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 666)
        contribution.delete()

        # Hourly contribution
        role = ContributorRole.objects.create(name="HourlyPerson", payment_type=2)
        HourlyRate.objects.create(role=role, rate=20)
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 20)
        contribution.delete()

        # Manual contribution
        role = ContributorRole.objects.create(name="ManualPerson", payment_type=3)
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        ManualRate.objects.create(contribution=contribution, rate=1000)
        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 1000)
        contribution.delete()


class ReportingApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ReportingApiTestCase, self).setUp()
        now = timezone.now()
        self.roles = {
            "FlatRate": ContributorRole.objects.create(name='Author', payment_type=0),
            "FeatureType": ContributorRole.objects.create(name='Author', payment_type=1),
            "Hourly": ContributorRole.objects.create(name='Author', payment_type=2),
            "Manual": ContributorRole.objects.create(name='Author', payment_type=3)
        }

        self.ft1 = FeatureType.objects.create(name="Surf Subs")
        self.ft2 = FeatureType.objects.create(name="Nasty Sandwiches")
        self.c1 = Content.objects.create(
            title="c1",
            feature_type=self.ft1,
            published=now-timezone.timedelta(days=3)
        )
        self.c2 = Content.objects.create(
            title="c2",
            feature_type=self.ft1,
            published=now-timezone.timedelta(days=4)
        )
        self.c3 = Content.objects.create(
            title="c3",
            feature_type=self.ft2,
            published=now-timezone.timedelta(days=5)
        )
        self.c4 = Content.objects.create(
            title="c4",
            feature_type=self.ft2,
            published=now - timezone.timedelta(days=6)
        )
        self.c5 = Content.objects.create(
            title="c5",
            published=now-timezone.timedelta(days=7)
        )
        User = get_user_model()
        self.a1 = User.objects.create(first_name='author', last_name='1', username='a1')
        self.a2 = User.objects.create(first_name='author', last_name='2', username='a2')
        self.a3 = User.objects.create(first_name='author', last_name='3', username='a3')
        self.a4 = User.objects.create(first_name='author', last_name='4', username='a4')
        self.a5 = User.objects.create(first_name='author', last_name='5', username='a 5')
        self.fp1 = FreelanceProfile.objects.create(contributor=self.a1)
        self.fp2 = FreelanceProfile.objects.create(contributor=self.a2)
        self.fp3 = FreelanceProfile.objects.create(contributor=self.a3)
        self.fp4 = FreelanceProfile.objects.create(contributor=self.a4)
        self.fp5 = FreelanceProfile.objects.create(contributor=self.a5)
        self.t1 = Tag.objects.create(name='Ballers')
        self.t2 = Tag.objects.create(name='Fallers')
        self.c1.authors.add(self.a1)
        self.c1.tags.add(self.t2)
        self.c1.save()
        self.c2.authors.add(self.a1)
        self.c2.tags.add(self.t1)
        self.c2.save()
        self.c3.authors.add(self.a2)
        self.c3.tags.add(self.t2)
        self.c3.save()
        self.c4.authors.add(self.a2)
        self.c4.tags.add(self.t1)
        self.c4.save()
        self.c5.authors.add(self.a2)
        self.c5.tags.add(self.t1, self.t2)
        self.c5.save()

        self.contributions = {
            'c1': [
                Contribution.objects.create(
                    role=self.roles['FlatRate'],
                    contributor=self.a1,
                    content=self.c1
                ),
                Contribution.objects.create(
                    role=self.roles['FeatureType'],
                    contributor=self.a2,
                    content=self.c1
                ),
                Contribution.objects.create(
                    role=self.roles['Hourly'],
                    contributor=self.a3,
                    content=self.c1
                ),
                Contribution.objects.create(
                    role=self.roles['Manual'],
                    contributor=self.a4,
                    content=self.c1
                )
            ],
            'c2': [
                Contribution.objects.create(
                    role=self.roles['FlatRate'],
                    contributor=self.a1,
                    content=self.c2
                ),
                Contribution.objects.create(
                    role=self.roles['FeatureType'],
                    contributor=self.a2,
                    content=self.c2
                ),
                Contribution.objects.create(
                    role=self.roles['Hourly'],
                    contributor=self.a3,
                    content=self.c2
                ),
                Contribution.objects.create(
                    role=self.roles['Manual'],
                    contributor=self.a4,
                    content=self.c2
                )
            ],
            'c3': [
                Contribution.objects.create(
                    role=self.roles['FlatRate'],
                    contributor=self.a1,
                    content=self.c3
                ),
                Contribution.objects.create(
                    role=self.roles['FeatureType'],
                    contributor=self.a2,
                    content=self.c3
                ),
                Contribution.objects.create(
                    role=self.roles['Hourly'],
                    contributor=self.a3,
                    content=self.c3
                ),
                Contribution.objects.create(
                    role=self.roles['Manual'],
                    contributor=self.a4,
                    content=self.c3
                )
            ],
            'c4': [
                Contribution.objects.create(
                    role=self.roles['FlatRate'],
                    contributor=self.a1,
                    content=self.c4
                ),
                Contribution.objects.create(
                    role=self.roles['FeatureType'],
                    contributor=self.a2,
                    content=self.c4
                ),
                Contribution.objects.create(
                    role=self.roles['Hourly'],
                    contributor=self.a3,
                    content=self.c4
                ),
                Contribution.objects.create(
                    role=self.roles['Manual'],
                    contributor=self.a4,
                    content=self.c4
                )
            ],
            'c5': [
                Contribution.objects.create(
                        role=self.roles['FlatRate'],
                        contributor=self.a1,
                        content=self.c5
                ),
                Contribution.objects.create(
                    role=self.roles['FeatureType'],
                    contributor=self.a2,
                    content=self.c5
                ),
                Contribution.objects.create(
                    role=self.roles['Hourly'],
                    contributor=self.a3,
                    content=self.c5
                ),
                Contribution.objects.create(
                    role=self.roles['Manual'],
                    contributor=self.a4,
                    content=self.c5
                )
            ]
        }

    def test_exclude_content_without_contributions(self):
        content = Content.objects.create(title='No contributions here')
        self.assertEqual(content.contributions.count(), 0)

        endpoint = reverse('contentreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(content.id, [cc['id'] for cc in resp.data])

    def test_content_filters(self):
        endpoint = reverse('contentreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': self.ft1.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

        resp = self.client.get(endpoint, {'feature_types': [self.ft1.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 4)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)

        resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug, self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        new_content = Content.objects.create(
            title='new content',
            published=timezone.now() - timezone.timedelta(days=3)
        )
        Contribution.objects.create(
            role=self.roles['FlatRate'],
            contributor=self.a5,
            content=new_content
        )

        # contributors filters
        resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a5.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_contribution_filters(self):
        endpoint = reverse('contributionreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 20)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': self.ft1.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 8)

        resp = self.client.get(endpoint, {'feature_types': [self.ft1.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 16)

        # Contributors filters
        resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 10)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 12)

        resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 12)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug, self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 20)

    def test_freelance_filters(self):
        endpoint = reverse('freelancereporting-list')

        new_feature_type = FeatureType.objects.create(name='New FeatureType')
        new_tag = Tag.objects.create(name='New Tag')
        new_content = Content.objects.create(
            title="This rules",
            feature_type=new_feature_type,
            published=timezone.now() - timezone.timedelta(days=1)
        )
        new_content.tags.add(new_tag)
        new_content.save()
        Contribution.objects.create(
            role=self.roles['FlatRate'],
            contributor=self.a5,
            content=new_content
        )

        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': new_feature_type.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

        resp = self.client.get(endpoint, {'feature_types': [new_feature_type.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)

        # Contributors filters
        resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

        resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

        resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

        resp = self.client.get(endpoint, {'tags': [new_tag.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

        resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 4)

        resp = self.client.get(endpoint, {'tags': [new_tag.slug, self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)
