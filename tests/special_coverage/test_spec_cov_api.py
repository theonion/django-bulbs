import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client

from bulbs.campaigns.models import Campaign
from bulbs.special_coverage.models import SpecialCoverage

from bulbs.utils.test import BaseAPITestCase, JsonEncoder


class SpecialCoverageApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(SpecialCoverageApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

    def test_special_coverage_detail(self):
        """Test retrieving a single special coverage object via URL."""

        special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query={},
            videos=[]
        )

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], special_coverage.id)

    def test_special_coverage_detail_permissions(self):
        """Ensure there is no unauthorized access to special coverage cms endpoints."""

        # create regular user
        regular_user_name = "regularuser"
        regular_user_pass = "12345"
        get_user_model().objects.create_user(
            regular_user_name,
            "regularguy@aol.com",
            regular_user_pass
        )
        self.client.login(username=regular_user_name, password=regular_user_pass)

        special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query={},
            videos=[]
        )

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 403)

    def test_query_dict_resolves_to_json_object_when_retrieving(self):
        """Check that query string does not resolve to a string when received by
        the frontend."""

        special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query={"included_ids": [1, 2, 3]},
            videos=[]
        )

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["query"], dict)

    def test_query_string_resolves_to_dict_when_saving(self):
        """Check that query string resolves back into a string when returned to the
        backend."""

        data_special_coverage = {
            "name": "something",
            "query": {
                "included_ids": [1, 2, 3]
            }
        }

        # post new listing
        self.client.post(
            reverse("special-coverage-list"),
            json.dumps(data_special_coverage, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertIsInstance(SpecialCoverage.objects.all()[0].query, dict)

    def test_slug_is_set_when_empty(self):
        """Check that the slug is set when there is currently no slug."""

        special_coverage_name = "somethin something something"
        data_special_coverage = {
            "name": special_coverage_name,
        }

        # post new listing
        response = self.client.post(
            reverse("special-coverage-list"),
            json.dumps(data_special_coverage, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(slugify(special_coverage_name), response.data["slug"])

    def test_slug_is_not_set_when_not_empty(self):
        """Check that the slug doesn't overwrite the current slug when already set."""

        special_coverage_slug = "somethin-something-something"
        data_special_coverage = {
            "name": "something whatever",
            "slug": special_coverage_slug
        }

        # post new listing
        response = self.client.post(
            reverse("special-coverage-list"),
            json.dumps(data_special_coverage, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(special_coverage_slug, response.data["slug"])

    def test_special_coverage_search_by_title(self):
        """Test that special coverages can be searched by their name."""

        # matching
        name = "Some name"
        special_coverage = SpecialCoverage.objects.create(name=name)

        # non-matching
        SpecialCoverage.objects.create(name="Joe Biden")

        response = self.client.get(reverse("special-coverage-list"), data={"search": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage.pk)

    def test_special_coverage_ordering_by_title(self):
        """Test that special coverage search results can be ordered by name."""

        special_coverage_3 = SpecialCoverage.objects.create(name="abc3")
        special_coverage_1 = SpecialCoverage.objects.create(name="abc1")
        special_coverage_2 = SpecialCoverage.objects.create(name="abc2")

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"search": "abc", "ordering": "name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)

    def test_special_coverage_search_by_campaign_sponsor_name(self):
        """Test that special coverages can be searched by their campaign's sponsor name."""

        # matching
        sponsor_name = "Hondaz"
        campaign = Campaign.objects.create(sponsor_name=sponsor_name)
        special_coverage = SpecialCoverage.objects.create(name="some special coverage",
                                                          campaign=campaign)

        # non-matching
        SpecialCoverage.objects.create(name="Joe Biden",
                                       campaign=Campaign.objects.create(sponsor_name="Hagendaz"))

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"search": sponsor_name})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage.pk)

    def test_special_coverage_ordering_by_campaign_sponsor_name(self):
        """Test that special coverage search results can be ordered by campaign's sponsor name."""

        special_coverage_3 = SpecialCoverage.objects.create(name="something something",
                                                            campaign=Campaign.objects.create(
                                                                sponsor_name="abc3"))
        special_coverage_1 = SpecialCoverage.objects.create(name="whateve3r",
                                                            campaign=Campaign.objects.create(
                                                                sponsor_name="abc1"))
        special_coverage_2 = SpecialCoverage.objects.create(name="this and that",
                                                            campaign=Campaign.objects.create(
                                                                sponsor_name="abc2"))

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"search": "abc", "ordering": "campaign__sponsor_name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)

    def test_special_coverage_search_by_campaign_label(self):
        """Test that special coverages can be searched by their campaign's label."""

        # matching
        campaign_label = "0-1337"
        campaign = Campaign.objects.create(campaign_label=campaign_label)
        special_coverage = SpecialCoverage.objects.create(name="some special coverage",
                                                          campaign=campaign)

        # non-matching
        SpecialCoverage.objects.create(name="Joe Biden",
                                       campaign=Campaign.objects.create(campaign_label="1-123"))

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"search": campaign_label})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage.pk)

    def test_special_coverage_ordering_by_campaign_label(self):
        """Test that special coverage search results can be ordered by campaign's label."""

        special_coverage_3 = SpecialCoverage.objects.create(name="something something",
                                                            campaign=Campaign.objects.create(
                                                                campaign_label="abc3"))
        special_coverage_1 = SpecialCoverage.objects.create(name="whateve3r",
                                                            campaign=Campaign.objects.create(
                                                                campaign_label="abc1"))
        special_coverage_2 = SpecialCoverage.objects.create(name="this and that",
                                                            campaign=Campaign.objects.create(
                                                                campaign_label="abc2"))

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"search": "abc", "ordering": "campaign__campaign_label"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)

    def test_special_coverage_search_by_status(self):
        """Test that special coverages can be searched by their status."""

        # matching
        special_coverage = SpecialCoverage.objects.create(name="some special coverage",
                                                          active=True,
                                                          promoted=False)

        # non-matching
        SpecialCoverage.objects.create(name="Joe Biden",
                                       active=False,
                                       promoted=True)

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"active": True, "promoted": False})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage.pk)

    def test_special_coverage_ordering_by_status(self):
        """Test that special coverage search results can be ordered by their status."""

        special_coverage_1 = SpecialCoverage.objects.create(name="Promoted",
                                                            active=True,
                                                            promoted=True)
        special_coverage_2 = SpecialCoverage.objects.create(name="Active but not promoted",
                                                            active=True,
                                                            promoted=False)
        special_coverage_3 = SpecialCoverage.objects.create(name="Not active",
                                                            active=False,
                                                            promoted=False)
        special_coverage_4 = SpecialCoverage.objects.create(name="Not really a valid state",
                                                            active=False,
                                                            promoted=True)

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"ordering": "active,promoted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)
        self.assertEqual(response.data["results"][3]["id"], special_coverage_4.pk)

    def test_special_coverage_persists_after_campaign_deletion(self):
        """Tests to make sure that a special coverage deletion does not delete a Campaign."""

        # Create campaign
        campaign = Campaign.objects.create(campaign_label="Birdman Stunna")

        # Create a special coverage object
        special_coverage = SpecialCoverage.objects.create(
            name="Jack Links is Covered",
            slug="jack-links-covered",
            description="jerky jokes",
            campaign=campaign
        )

        # Ensure campaign exists
        resp = self.client.get(reverse("campaign-detail", kwargs={"pk": campaign.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["campaign_label"], campaign.campaign_label)

        # Ensure special coverage exists
        resp = self.client.get(
            reverse("special-coverage-detail", kwargs={'pk': special_coverage.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], special_coverage.name)
        self.assertEqual(resp.data['campaign'], campaign.id)

        # Delete Campaign
        resp = self.client.delete(reverse("campaign-detail", kwargs={"pk": campaign.id}))
        self.assertEqual(resp.status_code, 204)
        self.assertIsNone(resp.data)

        # Check GET Campaign 404s
        resp = self.client.delete(reverse("campaign-detail", kwargs={"pk": campaign.id}))
        self.assertEqual(resp.status_code, 404)

        # Check GET SpecialCoverage 200
        resp = self.client.get(
            reverse("special-coverage-detail", kwargs={"pk": special_coverage.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["name"], special_coverage.name)
        self.assertEqual(resp.data["slug"], special_coverage.slug)
        self.assertEqual(resp.data["description"], special_coverage.description)
        self.assertIsNone(resp.data["campaign"])
