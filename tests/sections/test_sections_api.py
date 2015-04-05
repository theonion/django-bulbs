import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client

from bulbs.sections.models import Section

from bulbs.utils.test import  BaseAPITestCase, JsonEncoder


class SectionsApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(SectionsApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

    def test_sections_detail(self):
        """Test retrieving a single section object via URL."""

        # set up a test section
        section = Section.objects.create(
            name="Politics Politics",
            slug="politics-politics"
        )

        endpoint = reverse(
            "section-detail",
            kwargs={"pk": section.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], section.id)

    def test_sections_detail_permissions(self):
        """Ensure there is no unauthorized access to section cms endpoints."""

        # create regular user
        regular_user_name = "regularuser"
        regular_user_pass = "12345"
        get_user_model().objects.create_user(
            regular_user_name,
            "regularguy@aol.com",
            regular_user_pass
        )
        self.client.login(username=regular_user_name, password=regular_user_pass)

        section = Section.objects.create(
            name="Politics Politics",
            slug="politics-politics"
        )

        endpoint = reverse(
            "section-detail",
            kwargs={"pk": section.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 403)

    def test_query_dict_resolves_to_json_object_when_retrieving(self):
        """Check that query string does not resolve to a string when received by
        the frontend."""

        section = Section.objects.create(
            name="Politics Politics",
            slug="politics-politics",
            query={"included_ids": [1, 2, 3]}
        )

        endpoint = reverse(
            "section-detail",
            kwargs={"pk": section.id})
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data["query"], dict)

    def test_query_string_resolves_to_dict_when_saving(self):
        """Check that query string resolves back into a string when returned to the
        backend."""

        data_section = {
            "name": "something",
            "query": {
                "included_ids": [1, 2, 3]
            }
        }

        # post new listing
        self.client.post(
            reverse("section-list"),
            json.dumps(data_section, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertIsInstance(Section.objects.get(name="something").query, dict)

    def test_slug_is_set_when_empty(self):
        """Check that the slug is set when there is currently no slug."""

        section_name = "somethin something something"
        data_section = {
            "name": section_name,
        }

        # post new listing
        response = self.client.post(
            reverse("section-list"),
            json.dumps(data_section, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(slugify(section_name), response.data["slug"])

    def test_slug_is_not_set_when_not_empty(self):
        """Check that the slug doesn't overwrite the current slug when already set."""

        section_slug = "somethin-something-something"
        data_section = {
            "name": "something whatever",
            "slug": section_slug
        }

        # post new listing
        response = self.client.post(
            reverse("section-list"),
            json.dumps(data_section, cls=JsonEncoder),
            content_type="application/json"
        )

        self.assertEqual(section_slug, response.data["slug"])

    def test_section_search_by_name(self):
        """Test that searching sections by their name."""

        # matching
        name = "Some section name"
        section = Section.objects.create(name=name)

        # non-matching
        Section.objects.create(name="Joe Biden")

        response = self.client.get(reverse("section-list"), data={"search": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], section.pk)

    def test_section_ordering_by_name(self):
        """Test that section search results can be ordered by name."""

        section_3 = Section.objects.create(name="abc3")
        section_1 = Section.objects.create(name="abc1")
        section_2 = Section.objects.create(name="abc2")

        response = self.client.get(reverse("section-list"),
                                   data={"ordering": "name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], section_1.pk)
        self.assertEqual(response.data["results"][1]["id"], section_2.pk)
        self.assertEqual(response.data["results"][2]["id"], section_3.pk)
