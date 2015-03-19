from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.content.models import Content
from bulbs.special_coverage.models import SpecialCoverage

from tests.content.test_custom_search import BaseCustomSearchFilterTests
from tests.utils import BaseAPITestCase


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
            query="",
            videos=""
        )

        self.special_coverage.save()

    def test_special_coverage_detail(self):
        """Test retrieving a single special coverage object via URL."""

        endpoint = reverse(
            "special-coverage-detail",
            kwargs={"pk": self.special_coverage.id})
        response = self.client.get(endpoint)

        print(response.data["id"])

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


# TODO : test permissions for putting, posting, etc.


class SpecialCoverageQueryTests(BaseCustomSearchFilterTests):
    def setUp(self):
        super(SpecialCoverageQueryTests, self).setUp()

    def test_get_content(self):
        """tests the search results are instances of Content"""
        query = self.search_expectations[1][0]
        sc = SpecialCoverage.objects.create(
            name="All Obama, Baby",
            description="All Obama, Baby",
            query=query
        )
        res = sc.get_content()
        for content in res:
            assert isinstance(content, Content)

    def test_has_pinned_content(self):
        """tests that the .has_pinned_content accurately returns True or False"""
        query = self.search_expectations[0][0]
        sc = SpecialCoverage.objects.create(
            name="All Biden, Baby",
            description="All Biden, Baby",
            query=query
        )
        assert hasattr(sc, "has_pinned_content")
        assert sc.has_pinned_content is False
        query = self.search_expectations[-1][0]
        sc = SpecialCoverage.objects.create(
            name="Text query",
            description="Text query",
            query=query
        )
        assert hasattr(sc, "has_pinned_content")
        assert sc.has_pinned_content is True

    def test_contents(self):
        """tests that the .contents accurately returns Content objects"""
        query = self.search_expectations[2][0]
        sc = SpecialCoverage.objects.create(
            name="Obama and Biden, together",
            description="Obama and Biden, together",
            query=query
        )
        assert hasattr(sc, "contents")
        for content in sc.contents:
            assert isinstance(content, Content)
