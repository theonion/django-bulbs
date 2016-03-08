import mock

from django.utils import timezone

from bulbs.campaigns.models import Campaign
from bulbs.content.models import Content
from bulbs.sections.models import Section
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestReadingListObj


class BaseReadingListTestCase(BaseIndexableTestCase):
    """General configuration and data for ReadingListTestCases."""

    def setUp(self):
        super(BaseReadingListTestCase, self).setUp()
        self.recent_content = make_content(TestReadingListObj, published=self.now, _quantity=5)
        self.query_content = make_content(TestReadingListObj, published=self.now, _quantity=5)
        self.section = Section.objects.create(name="Local")
        self.unsponsored_special_coverage = SpecialCoverage.objects.create(
            name="soSpesh",
            start_date=self.now - timezone.timedelta(days=5),
            end_date=self.now + timezone.timedelta(days=5)
        )
        self.campaign = Campaign.objects.create(
            sponsor_name="Garbage",
            start_date=self.now - timezone.timedelta(days=10),
            end_date=self.now + timezone.timedelta(days=10),
        )
        self.sponsored_special_coverage = SpecialCoverage.objects.create(
            name="Sponsored",
            campaign=self.campaign,
            start_date=self.now - timezone.timedelta(days=7),
            end_date=self.now + timezone.timedelta(days=7),
        )
        Content.search_objects.refresh()

    def add_section_identifiers(self):
        self.section.query = {"included_ids": [obj.id for obj in self.query_content]}
        self.section.save()
        Content.search_objects.refresh()

    def add_unsponsored_special_coverage_identifiers(self):
        self.unsponsored_special_coverage.query = {
            "included_ids": [obj.id for obj in self.query_content]
        }
        self.unsponsored_special_coverage.save()
        Content.search_objects.refresh()

    def add_sponsored_special_coverage_identifiers(self):
        self.sponsored_special_coverage.query = {
            "included_ids": [obj.id for obj in self.query_content]
        }
        self.sponsored_special_coverage.save()
        Content.search_objects.refresh()


class ReadingListIdentifierTestCase(BaseReadingListTestCase):

    def test_recent_identifier(self):
        """Without association and if not popular, an object's identifier should be 'recent'"""
        for obj in self.recent_content:
            self.assertEqual(obj.reading_list_identifier, "recent")

    def test_section_identifier(self):
        # We want to confirm that sections trump recent.
        self.add_section_identifiers()
        for obj in self.query_content:
            self.assertEqual(obj.reading_list_identifier, self.section.es_id)

    def test_unsponsored_identifier(self):
        # We want to confirm that sections trump recent.
        self.add_section_identifiers()
        # We want to confirm that unsponsored special coverage trumps sections.
        self.add_unsponsored_special_coverage_identifiers()
        for obj in self.query_content:
            self.assertEqual(
                obj.reading_list_identifier, self.unsponsored_special_coverage.identifier
            )

    def test_popular_identifier(self):
        # We want to confirm that sections trump recent.
        self.add_section_identifiers()
        # We want to confirm that unsponsored special coverage trumps sections.
        self.add_unsponsored_special_coverage_identifiers()
        # We want to test that popular trumps unsponsored special coverages.
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = [obj.id for obj in self.query_content]
            for obj in self.query_content:
                self.assertEqual(obj.reading_list_identifier, "popular")

    def test_sponsored_special_coverage_identifier(self):
        # We want to confirm that sections trump recent.
        self.add_section_identifiers()
        # We want to confirm that unsponsored special coverage trumps sections.
        self.add_unsponsored_special_coverage_identifiers()
        # We want to test that popular trumps unsponsored special coverages.
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = [obj.id for obj in self.query_content]
            self.add_sponsored_special_coverage_identifiers()
            for obj in self.query_content:
                self.assertEqual(
                    obj.reading_list_identifier, self.sponsored_special_coverage.identifier
                )

