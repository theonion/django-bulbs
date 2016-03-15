import mock

from django.utils import timezone

from bulbs.content.models import Content
from bulbs.reading_list.popular import get_popular_ids, popular_content
from bulbs.utils.test import make_content, BaseIndexableTestCase


class PopularContentTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PopularContentTestCase, self).setUp()
        self.popular_content = make_content(
            published=self.now - timezone.timedelta(days=10), _quantity=10
        )
        self.recent_content = make_content(published=self.now, _quantity=10)
        self.expected_ingest_response = [obj.id for obj in self.popular_content]
        self.malformed_ingest_response = {obj.title: obj.id for obj in self.popular_content}
        Content.search_objects.refresh()

    def test_get_popular_ids_functioning(self):
        """Test Behavior when Ingest functioning."""
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = self.expected_ingest_response
            self.assertEqual(get_popular_ids(), self.expected_ingest_response)

    def test_get_popular_ids_connection_error(self):
        """Test Behavior when Ingest not functioning."""
        self.assertIsNone(get_popular_ids())

    def test_get_popular_content(self):
        """Test popular content query."""
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = self.expected_ingest_response
            eqs = popular_content()
            self.assertEqual(
                sorted([obj.id for obj in eqs.extra(size=eqs.count())]),
                get_popular_ids()
            )

    def test_get_popular_content_fallback(self):
        """Test recent fallback for popular content."""
        popular = popular_content()
        recent = Content.search_objects.search()
        for obj in popular.extra(size=popular.count()):
            self.assertIn(obj, recent.extra(size=recent.count()))

    def test_get_popular_content_error(self):
        """Test popular content return recent."""
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = self.expected_ingest_response
            eqs = popular_content()
            self.assertEqual(
                sorted([obj.id for obj in eqs.extra(size=eqs.count())]),
                get_popular_ids()
            )


class SpecialCoverageTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(SpecialCoverageTestCase, self).setUp()
