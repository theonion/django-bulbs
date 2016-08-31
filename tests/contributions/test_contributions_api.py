import csv
import json

from django.db.models import Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from elasticsearch_dsl import filter as es_filter
from freezegun import freeze_time
from six import StringIO

from bulbs.content.models import Content, FeatureType, Tag
from bulbs.contributions.models import (
    Contribution, ContributorRole, ManualRate, HourlyRate, FeatureTypeOverride,
    FlatRate, FlatRateOverride, FeatureTypeRate, FreelanceProfile, LineItem, OverrideProfile,
    ReportContent, Rate, RATE_PAYMENT_TYPES
)
from bulbs.contributions.serializers import RateSerializer
from bulbs.contributions.signals import *  # NOQA
from bulbs.utils.test import BaseAPITestCase, make_content

PAYMENT_TYPES = dict((label, value) for value, label in RATE_PAYMENT_TYPES)


class ContributionApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionApiTestCase, self).setUp()
        contributor_cls = get_user_model()
        self.feature_types = {
            "surfing": FeatureType.objects.create(name="Surfing"),
            "crying": FeatureType.objects.create(name="Crying")
        }

        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor"),
            "writer": ContributorRole.objects.create(name="Writer", payment_type=0),
            "featured": ContributorRole.objects.create(name="Featured", payment_type=1),
            "friend": ContributorRole.objects.create(name="Friend", payment_type=3)
        }

        self.contributors = {
            "jarvis": contributor_cls.objects.create(
                first_name="jarvis",
                last_name="monster",
                username="arduous"
            ),
            "marvin": contributor_cls.objects.create(
                first_name="marvin",
                last_name="complete",
                username="argyle"
            ),
        }
        for c in contributor_cls.objects.all():
            c.save()

    def test_contribution_indexed_on_content_create_and_update(self):
        client = Client()
        client.login(username="admin", password="secret")
        self.give_permissions()
        content_url = reverse("content-list")

        content_data = {
            "title": "WhyOhWhy",
            "foo": "help!",
            "authors": [{
                "first_name": self.contributors["jarvis"].first_name,
                "last_name": self.contributors["jarvis"].last_name,
                "username": self.contributors["jarvis"].username
            }]
        }
        content_url = reverse("content-list") + "?doctype=testcontent_testcontentobj"
        resp = client.post(
            content_url, json.dumps(content_data), content_type="application/json"
        )
        self.assertEquals(resp.status_code, 201)
        content_data = resp.data
        Contribution.search_objects.refresh()
        contribution = Contribution.objects.last()
        index = Contribution.search_objects.mapping.index
        doc_type = Contribution.search_objects.mapping.doc_type
        body = Contribution.search_objects.search().filter(
            es_filter.Terms(**{"id": [contribution.id]})
        ).to_dict()

        results = self.es.search(index, doc_type, body=body)
        published = results['hits']['hits'][0]['_source']['content']['published']
        self.assertIsNone(published)
        content_detail_url = reverse("content-detail", kwargs={"pk": content_data["id"]})
        expected_published = "2013-06-09T00:00:00-06:00"
        content_data.update({"published": expected_published})
        resp = client.put(
            content_detail_url, json.dumps(content_data), content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        Contribution.search_objects.refresh()

        results = self.es.search(index, doc_type, body=body)
        published = results['hits']['hits'][0]['_source']['content']['published']
        self.assertEqual(published, "2013-06-09T06:00:00+00:00")

    def test_content_authors_default_contribution(self):
        client = Client()
        client.login(username="admin", password="secret")

        self.give_permissions()

        endpoint = reverse("content-list")
        data = {


            "title": "howdy",
            "authors": [{
                "username": self.contributors["jarvis"].username,
                "first_name": self.contributors["jarvis"].first_name,
                "last_name": self.contributors["jarvis"].last_name,
                "id": self.contributors["jarvis"].id
            }]
        }
        resp = client.post(endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        id = resp.data.get('id')
        content = Content.objects.get(id=id)
        self.assertTrue(content.contributions.exists())
        jarvis_contribution = content.contributions.first()
        self.assertEqual(jarvis_contribution.role.name, 'Draft Writer')
        self.assertEqual(jarvis_contribution.contributor, self.contributors['jarvis'])
        self.assertEqual(jarvis_contribution.content, content)

        data.update(resp.data)
        data['authors'].append({
            "username": self.contributors["marvin"].username,
            "first_name": self.contributors["marvin"].first_name,
            "last_name": self.contributors["marvin"].last_name,
            "id": self.contributors["marvin"].id
        })
        detail_endpoint = reverse('content-detail', kwargs={'pk': id})
        resp = client.put(detail_endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(content.contributions.count(), 2)
        marvin_contribution = content.contributions.last()
        self.assertEqual(marvin_contribution.role.name, 'Draft Writer')
        self.assertEqual(marvin_contribution.contributor, self.contributors['marvin'])
        self.assertEqual(marvin_contribution.content, content)

    def test_contributionrole_api(self):
        client = Client()
        client.login(username="admin", password="secret")

        endpoint = reverse("contributorrole-list")
        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        payment_type = response.data[0].get('payment_type', None)
        self.assertEqual(payment_type, 'Manual')

        # Add some rates
        editor = self.roles.get("editor")
        editor_rate = FlatRate.objects.create(name=0, rate=100, role=editor)
        self.assertIsNotNone(editor_rate.updated_on)

        response = client.get(endpoint)
        self.assertEqual(response.status_code, 200)

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

        # Test Hourly
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

        profile1 = OverrideProfile.objects.create(
            role=self.roles["editor"],
            contributor=self.contributors["jarvis"]
        )
        profile2 = OverrideProfile.objects.create(
            role=self.roles["writer"],
            contributor=self.contributors["marvin"]
        )
        override1 = FlatRateOverride.objects.create(
            rate=60,
            profile=profile1
        )
        override2 = FlatRateOverride.objects.create(
            rate=50,
            profile=profile2
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
        self.assertEqual(resp.data.get("rate"), 70)
        self.assertEqual(resp.data.get("role").get("id"), self.roles["editor"].id)
        self.assertEqual(
            resp.data.get("contributor").get("id"), self.contributors["jarvis"].id
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

    def test_override_multiple_feature_types(self):
        endpoint = reverse('rate-overrides-list')
        client = Client()
        client.login(username='admin', password='secret')
        data = {
            'contributor': {
                'username': self.contributors['jarvis'].username,
                'id': self.contributors['jarvis'].id,
            },
            'role': self.roles['featured'].id,
            'feature_types': [{
                'rate': 80,
                'feature_type': self.feature_types["surfing"].name
            }]
        }
        resp = client.post(endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201)

        id = resp.data.get('id')
        detail_endpoint = reverse('rate-overrides-detail', kwargs={'pk': id})
        data.update(resp.data)
        data['feature_types'][0]['rate'] = 100

        data = {
            'contributor': {
                'username': self.contributors['jarvis'].username,
                'id': self.contributors['jarvis'].id,
            },
            'role': self.roles['featured'].id,
            'feature_types': [{
                'rate': 80,
                'feature_type': self.feature_types["surfing"].name
            }, {
                'rate': 90,
                'feature_type': self.feature_types["crying"].name
            }]
        }

        resp = client.put(detail_endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        feature_types = resp.data['feature_types']
        self.assertEqual(len(feature_types), 2)
        self.assertEqual(feature_types[0]['rate'], 90)
        self.assertEqual(OverrideProfile.objects.count(), 1)
        self.assertEqual(FeatureTypeOverride.objects.count(), 2)

    # TODO: custom validation if no feature_types for rates

    def test_override_delete_success(self):
        client = Client()
        client.login(username="admin", password="secret")

        profile = OverrideProfile.objects.create(
            contributor=self.contributors["jarvis"],
            role=self.roles["editor"]
        )

        # Override
        FlatRateOverride.objects.create(
            rate=100,
            profile=profile
        )

        endpoint = reverse("rate-overrides-detail", kwargs={"pk": profile.id})
        resp = client.get(endpoint)
        self.assertEqual(resp.status_code, 200)

        resp = client.delete(endpoint)
        self.assertEqual(resp.status_code, 204)

    def test_feature_type_override_list_success(self):
        client = Client()
        client.login(username="admin", password="secret")
        endpoint = reverse("rate-overrides-list")
        editor_ft_profile = OverrideProfile.objects.create(
            contributor=self.contributors["jarvis"],
            role=self.roles["editor"]
        )
        writer_ft_profile = OverrideProfile.objects.create(
            contributor=self.contributors["marvin"],
            role=self.roles["writer"]
        )
        f1 = FeatureType.objects.create(name="ha ha!")
        f2 = FeatureType.objects.create(name="no no.")
        editor_ft_profile.override_feature_type.create(rate=55, feature_type=f1)
        writer_ft_profile.override_feature_type.create(rate=55, feature_type=f2)
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
            "feature_types": [{
                "feature_type": {
                    "id": f1.id
                }
            }]
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

        content = make_content(authors=[])
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
        Contribution.search_objects.refresh()

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

        content = make_content(authors=[])
        Content.objects.get(id=content.id)
        endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        editor = self.roles["editor"]
        contribution = Contribution.objects.create(
            content=content,
            contributor=self.admin,
            role=editor
        )
        Contribution.search_objects.refresh()

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
        Contribution.search_objects.refresh()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate, {'id': flat.id, 'rate': 1, 'name': 'Flat Rate'})

        # change to FeatureType
        feature = FeatureType.objects.create(name='A Fun Feature For Kids!')
        content.feature_type = feature
        content.save()

        feature_rate = FeatureTypeRate.objects.get(
            role=self.roles['editor'],
            feature_type=feature,
        )
        feature_rate.rate = 50
        feature_rate.save()

        editor.payment_type = PAYMENT_TYPES['FeatureType']
        editor.save()
        Contribution.search_objects.refresh()
        response = client.get(endpoint)
        rate = response.data[0].get('rate')
        updated = rate.pop('updated_on')
        self.assertIsNotNone(updated)
        self.assertEqual(rate['id'], feature_rate.id)
        self.assertEqual(rate['rate'], 50)

        # change to Hourly
        editor.payment_type = PAYMENT_TYPES['Hourly']
        editor.save()
        Contribution.search_objects.refresh()
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

        rate_data = "667"
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
        self.assertEqual(contribution['role']['id'], self.roles["editor"].id)

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
            endpoint, json.dumps(contribution_data), content_type="application/json"
        )
        override_rate = response.data[0].get("override_rate")
        self.assertEqual(override_rate, 70)
        Contribution.search_objects.refresh()

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
        content = make_content(authors=[])
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
        content = make_content(authors=[], feature_type=feature_type)
        content_endpoint = reverse("content-contributions", kwargs={"pk": content.pk})

        # FlatRate contribution
        role = ContributorRole.objects.create(name="FlatRatePerson", payment_type=0)
        FlatRate.objects.create(role=role, rate=700)
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        Contribution.search_objects.refresh()

        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 700)
        contribution.delete()

        # FeatureType contribution
        role = ContributorRole.objects.create(name="FeatureTypePerson", payment_type=1)
        rate = FeatureTypeRate.objects.get(
            role=role,
            feature_type=feature_type,
        )
        rate.rate = 666
        rate.save()
        rate = FeatureTypeRate.objects.get(
            role=role,
            feature_type=feature_type_2
        )
        rate.rate = 444
        rate.save()
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        Contribution.search_objects.refresh()

        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 666)
        contribution.delete()
        Contribution.search_objects.refresh()

        # Hourly contribution
        role = ContributorRole.objects.create(name="HourlyPerson", payment_type=2)
        HourlyRate.objects.create(role=role, rate=20)
        contribution = Contribution.objects.create(
            content=content,
            role=role,
            contributor=self.admin
        )
        Contribution.search_objects.refresh()

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
        Contribution.search_objects.refresh()

        resp = client.get(content_endpoint)
        self.assertEqual(resp.status_code, 200)
        role_data = resp.data[0].get('role')
        self.assertEqual(role_data['rate'], 1000)
        contribution.delete()


class ReportingApiTestCase(BaseAPITestCase):
    def setUp(self):
        super(ReportingApiTestCase, self).setUp()
        self.freezer = freeze_time("2015-09-25")
        self.freezer.start()
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
            published=now - timezone.timedelta(days=3)
        )
        self.c2 = Content.objects.create(
            title="c2",
            feature_type=self.ft1,
            published=now - timezone.timedelta(days=4)
        )
        self.c3 = Content.objects.create(
            title="c3",
            feature_type=self.ft2,
            published=now - timezone.timedelta(days=5)
        )
        self.c4 = Content.objects.create(
            title="c4",
            feature_type=self.ft2,
            published=now - timezone.timedelta(days=6)
        )
        self.c5 = Content.objects.create(
            title="c5",
            published=now - timezone.timedelta(days=7)
        )
        usr_cls = get_user_model()
        self.a1 = usr_cls.objects.create(first_name='author', last_name='1', username='a1')
        self.a2 = usr_cls.objects.create(first_name='author', last_name='2', username='a2')
        self.a3 = usr_cls.objects.create(first_name='author', last_name='3', username='a3')
        self.a4 = usr_cls.objects.create(first_name='author', last_name='4', username='a4')
        self.a5 = usr_cls.objects.create(first_name='author', last_name='5', username='a5')
        self.fp1 = FreelanceProfile.objects.create(contributor=self.a1, payroll_name='aarvis')
        self.fp2 = FreelanceProfile.objects.create(contributor=self.a2, payroll_name='barvis')
        self.fp3 = FreelanceProfile.objects.create(contributor=self.a3, payroll_name='carvis')
        self.fp4 = FreelanceProfile.objects.create(contributor=self.a4, payroll_name='darvis')
        self.fp5 = FreelanceProfile.objects.create(contributor=self.a5, is_freelance=False)
        self.t1 = Tag.objects.create(name='Ballers')
        self.t2 = Tag.objects.create(name='Fallers')
        self.c1.authors.add(self.a1)
        self.c1.save()
        Content.search_objects.refresh()
        c1_a1_contribution = self.c1.contributions.filter(contributor=self.a1).first()
        c1_a1_contribution.role = self.roles['FlatRate']
        c1_a1_contribution.save()
        self.c1.tags.add(self.t2)
        self.c1.save()
        self.c2.authors.add(self.a1)
        c2_a1_contribution = self.c2.contributions.filter(contributor=self.a1).first()
        c2_a1_contribution.role = self.roles['FlatRate']
        c2_a1_contribution.save()
        self.c2.tags.add(self.t1)
        self.c2.save()
        self.c3.authors.add(self.a2)
        c3_a2_contribution = self.c3.contributions.filter(contributor=self.a2).first()
        c3_a2_contribution.role = self.roles['FeatureType']
        c3_a2_contribution.save()
        self.c3.tags.add(self.t2)
        self.c3.save()
        self.c4.authors.add(self.a2)
        c4_a2_contribution = self.c4.contributions.filter(contributor=self.a2).first()
        c4_a2_contribution.role = self.roles['FeatureType']
        c4_a2_contribution.save()
        self.c4.tags.add(self.t1)
        self.c4.save()
        self.c5.authors.add(self.a2)
        c5_a2_contribution = self.c5.contributions.filter(contributor=self.a2).first()
        c5_a2_contribution.role = self.roles['FeatureType']
        c5_a2_contribution.save()
        self.c5.tags.add(self.t1, self.t2)
        self.c5.save()

        self.contributions = {
            'c1': [
                c1_a1_contribution,
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
                c2_a1_contribution,
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
                c3_a2_contribution,
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
                c4_a2_contribution,
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
                c5_a2_contribution,
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
        LineItem.objects.create(
            contributor=self.a1, payment_date=self.now, amount=10
        )
        LineItem.objects.create(
            contributor=self.a2, payment_date=self.now, amount=10
        )
        LineItem.objects.create(
            contributor=self.a3,
            payment_date=self.now.replace(month=self.now.month + 1),
            amount=20
        )

        Contribution.search_objects.refresh()

    def tearDown(self):
        self.freezer.stop()
        super(ReportingApiTestCase, self).tearDown()

    def test_exclude_content_without_contributions(self):
        content = Content.objects.create(title='No contributions here')
        self.assertEqual(content.contributions.count(), 0)

        endpoint = reverse('contentreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(content.id, [cc['id'] for cc in resp.data['results']])

    def test_content_filters(self):
        ReportContent.search_objects.refresh()
        endpoint = reverse('contentreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': self.ft1.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)

        resp = self.client.get(endpoint, {'feature_types': [self.ft1.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 4)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 3)

        resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 3)

        resp = self.client.get(endpoint, {'tags': [self.t1.slug, self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        new_content = Content.objects.create(
            title='new content',
            published=timezone.now() - timezone.timedelta(days=3)
        )
        Contribution.objects.create(
            role=self.roles['FlatRate'],
            contributor=self.a5,
            content=new_content
        )

        ReportContent.search_objects.refresh()

        end_date = Content.objects.order_by(
            "-published"
        ).first().published.astimezone(
            timezone.get_current_timezone()
        )
        resp = self.client.get(endpoint, {"end": end_date})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 6)

        resp = self.client.get(endpoint, {"end": end_date - timezone.timedelta(days=1)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 4)

        resp = self.client.get(endpoint, {"end": str(end_date.date())})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 6)

        resp = self.client.get(
            endpoint, {"end": str((end_date - timezone.timedelta(days=1)).date())}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 4)

        start_date = Content.objects.order_by(
            "-published"
        ).first().published.astimezone(
            timezone.get_current_timezone()
        )
        resp = self.client.get(endpoint, {"start": start_date})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

        resp = self.client.get(endpoint, {"start": start_date - timezone.timedelta(days=1)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 3)

        resp = self.client.get(endpoint, {"start": str(start_date.date())})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

        resp = self.client.get(
            endpoint, {"start": str((start_date - timezone.timedelta(days=1)).date())}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 3)

        # contributors filters
        # resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 5)

        # resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 5)

        # resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 5)

        # resp = self.client.get(endpoint, {'contributors': [self.a5.username]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 1)

        # resp = self.client.get(endpoint, {'staff': 'freelance'})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data), 5)

        # resp = self.client.get(endpoint, {'staff': 'staff'})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data), 1)

    def test_contribution_filters(self):
        Contribution.search_objects.refresh()
        endpoint = reverse('contributionreporting-list')
        resp = self.client.get(endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 20)

        # ordering by user
        resp = self.client.get(endpoint, {'ordering': 'user'})
        self.assertEqual(resp.status_code, 200)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': self.ft1.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 8)

        resp = self.client.get(endpoint, {'feature_types': [self.ft1.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 16)

        # Contributors filters
        resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 10)

        # TODO: Fix the goddamn tag query
        # resp = self.client.get(endpoint, {'tags': [self.t1.slug]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 12)

        # resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 12)

        # resp = self.client.get(endpoint, {'tags': [self.t1.slug, self.t2.slug]})
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(len(resp.data['results']), 20)

        new_content = Content.objects.create(
            title='new content',
            published=timezone.now() - timezone.timedelta(days=3)
        )
        Contribution.objects.create(
            role=self.roles['FlatRate'],
            contributor=self.a5,
            content=new_content
        )
        Contribution.search_objects.refresh()

        resp = self.client.get(endpoint, {'staff': 'freelance'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 20)

        resp = self.client.get(endpoint, {'staff': 'staff'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        latest_content = Content.objects.all().order_by("-published").first()
        end_date = (
            self.c2.published.astimezone(
                timezone.get_current_timezone()
            ) - timezone.timedelta(seconds=1)
        ).date()
        resp = self.client.get(endpoint, {"end": str(end_date)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 16)

        resp = self.client.get(endpoint, {"end": str(latest_content.published)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 21)

        latest_content = Content.objects.all().order_by("-published").first()
        start_date = (
            latest_content.published.astimezone(
                timezone.get_current_timezone()
            ) + timezone.timedelta(seconds=1)
        )
        resp = self.client.get(endpoint, {"start": start_date})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 5)

        latest_content = Content.objects.all().order_by("-published").first()
        start_date = (
            latest_content.published.astimezone(timezone.get_current_timezone()) -
            timezone.timedelta(days=1)
        ).date()
        resp = self.client.get(endpoint, {"start": start_date})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 9)

        start_date = latest_content.published.astimezone(timezone.get_current_timezone())
        resp = self.client.get(endpoint, {"start": str(start_date)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 5)

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
        self.assertEqual(len(resp.data['results']), 5)

        # Feature Type filters
        resp = self.client.get(endpoint, {'feature_types': new_feature_type.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        resp = self.client.get(endpoint, {'feature_types': [new_feature_type.slug, self.ft2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        # Contributors filters
        resp = self.client.get(endpoint, {'contributors': [self.a1.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        resp = self.client.get(endpoint, {'contributors': [self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        resp = self.client.get(endpoint, {'contributors': [self.a1.username, self.a2.username]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)

        resp = self.client.get(endpoint, {'tags': [new_tag.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

        resp = self.client.get(endpoint, {'tags': [self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 4)

        resp = self.client.get(endpoint, {'tags': [new_tag.slug, self.t2.slug]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 5)

        new_content = Content.objects.create(
            title='new content',
            published=timezone.now() - timezone.timedelta(days=3)
        )
        Contribution.objects.create(
            role=self.roles['FlatRate'],
            contributor=self.a5,
            content=new_content
        )

        resp = self.client.get(endpoint, {'staff': 'freelance'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 4)

        resp = self.client.get(endpoint, {'staff': 'staff'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)

    def test_line_item_reporting(self):
        endpoint = reverse("line-item-reporting-list")
        self.assertEqual(endpoint, "/api/v1/contributions/line-item-reporting/")

        start_date = self.now.replace(day=1, hour=0, minute=0, second=0)
        end_date = start_date.replace(month=start_date.month + 1) - timezone.timedelta(seconds=1)

        resp = self.client.get(
            endpoint,
            data={
                "format": "csv",
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        )
        self.assertEqual(resp.status_code, 200)
        csvreader = csv.reader(StringIO(''.join(v.decode('utf-8')
                                                for v in resp.streaming_content)))
        # Check Header
        self.assertEqual(next(csvreader),
                         ['Payment Date', 'Payroll Name', 'Amount', 'Note'])

        rows = [r for r in csvreader]
        self.assertEqual(2, len(rows))


class FlatRateAPITestCase(BaseAPITestCase):
    """
    Tests for FlatRate API Endpoint.
    """
    def setUp(self):
        super(FlatRateAPITestCase, self).setUp()
        self.role = ContributorRole.objects.create(
            name="GarbageGuy",
            payment_type=0
        )
        self.list_endpoint = reverse("flat-rate-list", kwargs={"role_pk": self.role.pk})

    def test_list_route(self):
        self.assertEqual(
            self.list_endpoint, "/api/v1/contributions/role/{}/flat_rates/".format(self.role.id)
        )

    def test_detail_route(self):
        endpoint = reverse("flat-rate-detail", kwargs={"role_pk": 1, "pk": 1})
        self.assertEqual(endpoint, "/api/v1/contributions/role/1/flat_rates/1/")

    def test_post_success(self):
        data = {"rate": 200}
        resp = self.api_client.post(self.list_endpoint, data=data)
        self.assertEqual(resp.status_code, 201)
        rate = FlatRate.objects.last()
        self.assertEqual(resp.data, {"id": rate.id, "rate": 200})

    def test_list_order(self):
        """The most recently updated should be at the top of the list."""
        for i in range(40):
            FlatRate.objects.create(rate=i, role=self.role)
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        rate_max = FlatRate.objects.all().aggregate(Max('rate'))
        rate = FlatRate.objects.get(rate=rate_max["rate__max"])
        top_id = resp.data["results"][0]["id"]
        self.assertEqual(rate.id, top_id)

    def test_role_filter(self):
        """Results should be filtered on the role_pk provided in the url"""
        another_role = ContributorRole.objects.create(name="Welcome King", payment_type=1)
        for i in range(20):
            FlatRate.objects.create(rate=i, role=self.role)
            FlatRate.objects.create(rate=i, role=another_role)
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(FlatRate.objects.get(id=id).role, self.role)

        another_role_list_endpoint = reverse("flat-rate-list", kwargs={"role_pk": another_role.pk})
        resp = self.api_client.get(another_role_list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(FlatRate.objects.get(id=id).role, another_role)


class HourlyRateAPITestCase(BaseAPITestCase):
    """
    Tests for HourlyRate API Endpoint.
    """
    def setUp(self):
        super(HourlyRateAPITestCase, self).setUp()
        self.role = ContributorRole.objects.create(
            name="GarbageGuy",
            payment_type=2
        )
        self.list_endpoint = reverse("hourly-rate-list", kwargs={"role_pk": self.role.pk})

    def test_list_route(self):
        self.assertEqual(
            self.list_endpoint, "/api/v1/contributions/role/{}/hourly_rates/".format(self.role.id)
        )

    def test_detail_route(self):
        endpoint = reverse("hourly-rate-detail", kwargs={"role_pk": self.role.id, "pk": 1})
        self.assertEqual(
            endpoint, "/api/v1/contributions/role/{}/hourly_rates/1/".format(self.role.id)
        )

    def test_post_success(self):
        data = {"rate": 200}
        resp = self.api_client.post(self.list_endpoint, data=data)
        self.assertEqual(resp.status_code, 201)
        rate = HourlyRate.objects.last()
        self.assertEqual(resp.data, {"id": rate.id, "rate": 200})

    def test_list_order(self):
        """The most recently updated should be at the top of the list."""
        for i in range(40):
            HourlyRate.objects.create(rate=i, role=self.role)
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        rate_max = HourlyRate.objects.all().aggregate(Max('rate'))
        rate = HourlyRate.objects.get(rate=rate_max["rate__max"])
        top_id = resp.data["results"][0]["id"]
        self.assertEqual(rate.id, top_id)

    def test_role_filter(self):
        """Results should be filtered on the role_pk provided in the url"""
        another_role = ContributorRole.objects.create(name="Welcome King", payment_type=2)
        for i in range(20):
            HourlyRate.objects.create(rate=i, role=self.role)
            HourlyRate.objects.create(rate=i, role=another_role)
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(HourlyRate.objects.get(id=id).role, self.role)

        another_role_list_endpoint = reverse(
            "hourly-rate-list", kwargs={"role_pk": another_role.pk}
        )
        resp = self.api_client.get(another_role_list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(HourlyRate.objects.get(id=id).role, another_role)


class FeatureTypeRateAPITestCase(BaseAPITestCase):
    """
    Tests for HourlyRate API Endpoint.
    """
    def setUp(self):
        super(FeatureTypeRateAPITestCase, self).setUp()
        self.role = ContributorRole.objects.create(
            name="GarbageGuy",
            payment_type=1
        )
        self.feature_type = FeatureType.objects.create(name="Surf")
        self.list_endpoint = reverse("feature-type-rate-list", kwargs={"role_pk": self.role.pk})

    def test_list_route(self):
        self.assertEqual(
            self.list_endpoint,
            "/api/v1/contributions/role/{}/feature_type_rates/".format(self.role.id)
        )

    def test_detail_route(self):
        endpoint = reverse("feature-type-rate-detail", kwargs={"role_pk": 1, "pk": 1})
        self.assertEqual(endpoint, "/api/v1/contributions/role/1/feature_type_rates/1/")

    def test_put_success(self):
        data = {"rate": 200, "feature_type": "surf"}
        rr = self.role.feature_type_rates.filter(feature_type__slug="surf").first()
        endpoint = reverse(
            "feature-type-rate-detail", kwargs={"role_pk": self.role.id, "pk": rr.id}
        )
        resp = self.api_client.put(endpoint, data=data)
        self.assertEqual(resp.status_code, 200)
        rate = FeatureTypeRate.objects.last()
        self.assertEqual(resp.data, {"id": rate.id, "rate": 200, "feature_type": "Surf"})

    def test_list_order(self):
        """The most recently updated should be at the top of the list."""
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        another_role = ContributorRole.objects.create(name="RoleTide", payment_type=1)
        for i in alphabet:
            ft = FeatureType.objects.create(name=i)
            ftr1 = FeatureTypeRate.objects.get(role=another_role, feature_type=ft)
            ftr1.rate = 20
            ftr1.save()
            ftr2 = FeatureTypeRate.objects.get(role=self.role, feature_type=ft)
            ftr2.rate = 20
            ftr2.save()
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], FeatureType.objects.count())

        ordered_feature_types = [
            feature_type.name for feature_type in FeatureType.objects.all().order_by('name')
        ]
        feature_type = None
        for obj in resp.data["results"]:
            new_feature_type = obj.get("feature_type")
            if not feature_type:
                pass
            else:
                self.assertGreater(
                    ordered_feature_types.index(new_feature_type),
                    ordered_feature_types.index(feature_type)
                )
            feature_type = new_feature_type

    def test_role_filter(self):
        """Results should be filtered on the role_pk provided in the url"""
        another_role = ContributorRole.objects.create(name="Welcome King", payment_type=2)
        rr = FeatureTypeRate.objects.get(role=self.role, feature_type=self.feature_type)
        rr.rate = 20
        rr.save()
        rr = FeatureTypeRate.objects.get(role=another_role, feature_type=self.feature_type)
        rr.rate = 21
        rr.save()
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(FeatureTypeRate.objects.get(id=id).role, self.role)

        another_role_list_endpoint = reverse(
            "feature-type-rate-list", kwargs={"role_pk": another_role.pk}
        )
        resp = self.api_client.get(another_role_list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        for resp_rate in resp.data["results"]:
            id = resp_rate.get("id")
            self.assertEqual(FeatureTypeRate.objects.get(id=id).role, another_role)


class DuplicateContributionTestCase(BaseAPITestCase):
    """
    VERY annoying bug where save triggers *some* duplicate contributions for larger querysets.
    Trying to emulate the conditions as best I can.
    """

    def setUp(self):
        super(DuplicateContributionTestCase, self).setUp()
        self.user_cls = get_user_model()
        self.draft_writer = ContributorRole.objects.create(
            name='Draft Writer',
            payment_type=1
        )
        self.feature_type = FeatureType.objects.create(name='Example')
        rate = self.feature_type.feature_type_rates.all()[0]
        rate.rate = 25
        rate.save()
        self.content = Content.objects.create(
            title='God help us',
            feature_type=self.feature_type,
            published=self.now
        )
        self.contribution_endpoint = reverse(
            "content-contributions",
            kwargs={"pk": self.content.pk}
        )
        for i in range(30):
            self.user_cls.objects.create(
                username='user:{}'.format(i),
                email='{0}@{1}.com'.format(i, i),
                first_name='first_name:{}'.format(i),
                last_name='last_name:{}'.format(i),
                is_active=True,
                is_staff=True
            )
        self.content.contributions.all().delete()
        Content.search_objects.refresh()

    def test_ten_no_duplicate_delete(self):
        self._test_quantity(_quantity=10)
        self._test_delete(_quantity=2)

    def _test_delete(self, _quantity=0):
        original_count = self.content.contributions.count()
        resp = self.api_client.get(
            self.contribution_endpoint,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        for i in range(_quantity):
            data.pop()

        resp2 = self.api_client.post(
            self.contribution_endpoint,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.data), original_count - _quantity)

    def _test_quantity(self, _quantity=0):
        # check empty
        resp1 = self.api_client.get(self.contribution_endpoint)
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.data), 0)
        self.update_contributions(_quantity=_quantity)

        # GET before POST
        resp2 = self.api_client.get(
            self.contribution_endpoint,
            content_type='application/json',
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.data), _quantity)

        # check POST response
        resp3 = self.api_client.post(
            self.contribution_endpoint,
            data=json.dumps(resp2.data),
            content_type="application/json",
        )
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(len(resp3.data), _quantity)

        # GET after POST
        resp4 = self.api_client.get(
            self.contribution_endpoint,
            content_type='application/json'
        )
        self.assertEqual(resp4.status_code, 200)
        self.assertEqual(len(resp4.data), _quantity)

    def update_contributions(self, _quantity=0):
        user_qs = self.user_cls.objects.all()
        for i in range(_quantity):
            self.content.contributions.create(
                contributor=user_qs[i % user_qs.count()],
                role=self.draft_writer
            )
        Contribution.search_objects.refresh()
