import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseAPITestCase, JsonEncoder


class SpecialCoverageApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(SpecialCoverageApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

        # set up a test special coverage
        self.special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query={},
            videos=[],
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

    def test_query_dict_resolves_to_json_object_when_retrieving(self):
        """Check that query string does not resolve to a string when received by
        the frontend."""

        self.special_coverage.query = {"included_ids": [1, 2, 3]}
        self.special_coverage.save()

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": self.special_coverage.id})
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

    def test_query_string_filters_null_values_when_saving(self):
        """Andrew Kos comments on tests. I however, do not."""

        group = {
            "conditions": [
                {
                    "values": [{
                        "value": 'test',
                        "label": 'test'
                    }],
                    "type": "all",
                    "field": "tag"
                },
            ],
        }
        data = {
            "name": "special boy cammy",
            "query": {
                "pinned_ids": [1, 2, 3, None],
                "excluded_ids": [4, 5, 6, None],
                "groups": [group, None],
                "included_ids": [7, 8, 9, None]
            }
        }

        resp = self.client.post(
            reverse("special-coverage-list"),
            json.dumps(data, cls=JsonEncoder),
            content_type="application/json"
        )
        query = resp.data.get("query")
        pinned_ids = query.get("pinned_ids")
        excluded_ids = query.get("excluded_ids")
        groups = query.get("groups")
        included_ids = query.get("included_ids")
        self.assertEqual(pinned_ids, [1, 2, 3])
        self.assertEqual(excluded_ids, [4, 5, 6])
        self.assertEqual(groups, [group])
        self.assertEqual(included_ids, [7, 8, 9])
