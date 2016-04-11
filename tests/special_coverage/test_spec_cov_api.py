import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client
from django.utils import timezone

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.methods import today
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
        )

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": special_coverage.id})
        response = self.client.get(endpoint)

        response_data = json.loads(response.content.decode("utf8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["id"], special_coverage.id)
        self.assertTrue(isinstance(response_data["videos"], list))

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

    def test_special_coverage_search_by_status(self):
        """Test that special coverages can be searched by their status."""

        today_in_variable_form_for_mike_parent = today()

        # matching
        special_coverage = SpecialCoverage.objects.create(
            name="some special coverage",
            start_date=today_in_variable_form_for_mike_parent - timezone.timedelta(days=2),
            end_date=today_in_variable_form_for_mike_parent + timezone.timedelta(days=2),
            promoted=False
        )

        # non-matching
        SpecialCoverage.objects.create(
            name="Joe Biden",
            start_date=today_in_variable_form_for_mike_parent - timezone.timedelta(days=5),
            end_date=today_in_variable_form_for_mike_parent - timezone.timedelta(days=3),
            promoted=True
        )

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"active": True, "promoted": False})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage.pk)

    def test_special_coverage_ordering_by_status(self):
        """Test that special coverage search results can be ordered by their status."""

        special_coverage_1 = SpecialCoverage.objects.create(name="Promoted",
                                                            active=False,
                                                            promoted=False)
        special_coverage_2 = SpecialCoverage.objects.create(name="Active but not promoted",
                                                            active=False,
                                                            promoted=True)
        special_coverage_3 = SpecialCoverage.objects.create(name="Not active",
                                                            active=True,
                                                            promoted=False)
        special_coverage_4 = SpecialCoverage.objects.create(name="Not really a valid state",
                                                            active=True,
                                                            promoted=True)

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"ordering": "active,promoted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)
        self.assertEqual(response.data["results"][3]["id"], special_coverage_4.pk)

    def test_special_coverage_ordering_by_status_reverse(self):
        """Test that special coverage search results can be ordered by their status
        in reverse."""

        special_coverage_1 = SpecialCoverage.objects.create(name="Promoted",
                                                            active=True,
                                                            promoted=True)
        special_coverage_2 = SpecialCoverage.objects.create(name="Active but not promoted",
                                                            active=True,
                                                            promoted=False)
        special_coverage_3 = SpecialCoverage.objects.create(name="Not active",
                                                            active=False,
                                                            promoted=True)
        special_coverage_4 = SpecialCoverage.objects.create(name="Not really a valid state",
                                                            active=False,
                                                            promoted=False)

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"ordering": "-active,-promoted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)
        self.assertEqual(response.data["results"][1]["id"], special_coverage_2.pk)
        self.assertEqual(response.data["results"][2]["id"], special_coverage_3.pk)
        self.assertEqual(response.data["results"][3]["id"], special_coverage_4.pk)

    def test_active_and_promoted_lowercase_boolean(self):
        """Tests that filter backend can correctly evaluate 'true' and 'false'."""

        today_in_variable_form_for_mike_parent = today()

        special_coverage_1 = SpecialCoverage.objects.create(
            name="Promoted",
            start_date=today_in_variable_form_for_mike_parent - timezone.timedelta(days=1),
            end_date=today_in_variable_form_for_mike_parent + timezone.timedelta(days=1),
            promoted=True
        )
        special_coverage_2 = SpecialCoverage.objects.create(
            name="Not active or promoted",
            start_date=today_in_variable_form_for_mike_parent + timezone.timedelta(days=1),
            end_date=today_in_variable_form_for_mike_parent + timezone.timedelta(days=2),
            promoted=False
        )

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"active": "true", "promoted": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_1.pk)

        response = self.client.get(reverse("special-coverage-list"),
                                   data={"active": "false", "promoted": "false"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], special_coverage_2.pk)

    def test_special_coverage_detail_image(self):
        """Test adding detail image content to a special coverage."""
        data = {
            "name": "Special Coverage",
            "query": {
                "included_ids": [1, 2, 3]
            },
            "image": {
                "id": 123,
                "alt": "A photo",
                "caption": "A caption"
            },
        }
        resp = self.client.post(
            reverse("special-coverage-list"),
            json.dumps(data, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["image"]["id"], 123)
        self.assertEqual(resp.data["image"]["alt"], "A photo")
        self.assertEqual(resp.data["image"]["caption"], "A caption")

        # get SC and check if image serializes correctly
        resp = self.client.get(
            reverse("special-coverage-detail", kwargs={"pk": resp.data["id"]}))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["image"]["id"], 123)
        self.assertEqual(resp.data["image"]["alt"], "A photo")
        self.assertEqual(resp.data["image"]["caption"], "A caption")
