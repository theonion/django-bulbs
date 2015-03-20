from bulbs.content.models import Content
from bulbs.special_coverage.models import SpecialCoverage

from tests.content.test_custom_search import BaseCustomSearchFilterTests


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
            self.assertIsInstance(content, Content)

    def test_has_pinned_content(self):
        """tests that the .has_pinned_content accurately returns True or False"""

        query = self.search_expectations[0][0]
        sc = SpecialCoverage.objects.create(
            name="All Biden, Baby",
            description="All Biden, Baby",
            query=query
        )

        self.assertTrue(hasattr(sc, "has_pinned_content"))
        self.assertFalse(sc.has_pinned_content)

        query = self.search_expectations[-1][0]
        sc = SpecialCoverage.objects.create(
            name="Text query",
            description="Text query",
            query=query
        )

        self.assertTrue(hasattr(sc, "has_pinned_content"))
        self.assertTrue(sc.has_pinned_content)

    def test_contents(self):
        """tests that the .contents accurately returns Content objects"""

        query = self.search_expectations[2][0]
        sc = SpecialCoverage.objects.create(
            name="Obama and Biden, together",
            description="Obama and Biden, together",
            query=query
        )

        self.assertTrue(hasattr(sc, "contents"))
        for content in sc.contents:
            self.assertIsInstance(content, Content)
