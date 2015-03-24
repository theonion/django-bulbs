import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.campaigns.models import Campaign
from bulbs.special_coverage.models import SpecialCoverage

from tests.utils import BaseAPITestCase, JsonEncoder


class SpecialCoverageApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(SpecialCoverageApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

        # set up a test special coverage
        self.campaign = Campaign.objects.create(
            sponsor_name="Jack Links"
        )
        self.special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query="",
            videos="",
            campaign=self.campaign
        )

        self.special_coverage.save()

    def test_special_coverage_detail(self):
        """Test retrieving a single special coverage object via URL."""

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": self.special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.special_coverage.id)

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

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": self.special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 403)

    def test_query_string_resolves_to_json_object_when_retrieving(self):
        """Check that query string does not resolve to a string when received by
        the frontend."""

        self.special_coverage.query = '{"included_ids": [1,2,3]}'
        self.special_coverage.save()

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": self.special_coverage.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["query"], dict)

    def test_query_string_resolves_to_string_when_saving(self):
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

        self.assertIsInstance(SpecialCoverage.objects.all()[0].query, basestring)
