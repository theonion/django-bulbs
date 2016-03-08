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


class ReadingListContextTestCase(BaseReadingListTestCase):

    def test_recent(self):
        example = Content.objects.first()
        self.assertEqual(example.reading_list_identifier, "recent")

        context = example.get_reading_list_context()
        self.assertEqual(context["name"], "Recent News")
        self.assertEqual(context["targeting"], {})
        self.assertEqual(context["videos"], [])
        content = context["content"]
        self.assertIsNotNone(content)
        body = content.to_dict()

        # Sorted by descending publish date.
        self.assertEqual(
            body["sort"],
            [{"published": {"order": "desc"}}, {"last_modified": {"order": "desc"}}]
        )

        # Query excludes the current object.
        self.assertIn(
            {"ids": {"values": [example.id]}},
            body["query"]["filtered"]["filter"]["bool"]["must_not"]
        )

        # All expected Ids match.
        reading_list = sorted([example.id] + [obj.id for obj in content])
        self.assertEqual(
            reading_list, sorted([obj.id for obj in self.query_content])
        )

    def test_section(self):
        self.add_section_identifiers()

        example = Content.objects.first()
        self.assertEqual(example.reading_list_identifier, self.section.es_id)

        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.section.name)
        self.assertEqual(context["targeting"], {})
        self.assertEqual(context["videos"], [])
        content = context["content"]
        self.assertIsNotNone(content)
        body = content.to_dict()

        # Sorted by descending publish date.
        self.assertEqual(body["sort"], [{"published": {"order": "desc"}}])

        # Query excludes the current object.
        self.assertIn(
            {"ids": {"values": [example.id]}},
            body["query"]["filtered"]["filter"]["bool"]["must_not"]
        )

        # All expected Ids match.
        reading_list = sorted([example.id] + [obj.id for obj in content])
        self.assertEqual(
            reading_list, sorted([obj.id for obj in self.query_content])
        )

    def test_unsponsored_special_coverage(self):
        self.add_section_identifiers()
        self.add_unsponsored_special_coverage_identifiers()

        example = Content.objects.first()
        self.assertEqual(
            example.reading_list_identifier, self.unsponsored_special_coverage.identifier
        )

        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.unsponsored_special_coverage.name)
        self.assertEqual(
            context["targeting"]["dfp_specialcoverage"], self.unsponsored_special_coverage.slug
        )
        self.assertEqual(context["videos"], self.unsponsored_special_coverage.videos)
        content = context["content"]
        self.assertIsNotNone(content)
        body = content.to_dict()

        # Sorted by descending publish date.
        self.assertEqual(body["sort"], ["_score", {"published": {"order": "desc"}}])

        # Query excludes the current object.
        self.assertIn(
            {"ids": {"values": [example.id]}},
            body["query"]["filtered"]["filter"]["bool"]["must_not"]
        )

        # All expected Ids match.
        reading_list = sorted([example.id] + [obj.id for obj in content])
        self.assertEqual(
            reading_list, sorted([obj.id for obj in self.query_content])
        )

    def test_popular(self):
        self.add_section_identifiers()
        self.add_unsponsored_special_coverage_identifiers()

        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = [obj.id for obj in self.query_content]
            example = Content.objects.first()
            self.assertEqual(example.reading_list_identifier, "popular")

            context = example.get_reading_list_context()
            self.assertEqual(context["name"], "popular")
            self.assertEqual(context["targeting"], {})
            self.assertEqual(context["videos"], [])
            content = context["content"]
            self.assertIsNotNone(content)
            body = content.to_dict()

            # Sorted by descending publish date.
            self.assertEqual(
                body["sort"],
                [{"published": {"order": "desc"}}, {"last_modified": {"order": "desc"}}]
            )

            # Query excludes the current object.
            self.assertIn(
                {"ids": {"values": [example.id]}},
                body["query"]["filtered"]["filter"]["bool"]["must_not"]
            )

            # All expected Ids match.
            reading_list = sorted([example.id] + [obj.id for obj in content])
            self.assertEqual(
                reading_list, sorted([obj.id for obj in self.query_content])
            )

    def test_sponsored_special_coverage(self):
        self.add_section_identifiers()
        self.add_unsponsored_special_coverage_identifiers()
        self.add_sponsored_special_coverage_identifiers()

        example = Content.objects.first()
        self.assertEqual(
            example.reading_list_identifier, self.sponsored_special_coverage.identifier
        )

        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.sponsored_special_coverage.name)
        self.assertEqual(
            context["targeting"]["dfp_specialcoverage"], self.sponsored_special_coverage.slug
        )
        self.assertEqual(context["targeting"]["dfp_campaign"], self.campaign.campaign_label)
        self.assertEqual(context["targeting"]["dfp_campaign_id"], self.campaign.id)
        self.assertEqual(context["videos"], self.sponsored_special_coverage.videos)
        content = context["content"]
        self.assertIsNotNone(content)
        body = content.to_dict()

        # Sorted by descending publish date.
        self.assertEqual(body["sort"], ["_score", {"published": {"order": "desc"}}])

        # Query excludes the current object.
        self.assertIn(
            {"ids": {"values": [example.id]}},
            body["query"]["filtered"]["filter"]["bool"]["must_not"]
        )

        # All expected Ids match.
        reading_list = sorted([example.id] + [obj.id for obj in content])
        self.assertEqual(
            reading_list, sorted([obj.id for obj in self.query_content])
        )


class ReadingListIdentifierTestCase(BaseReadingListTestCase):

    def test_recent_identifier(self):
        """Without association and if not popular, an object's identifier should be 'recent'"""
        for obj in self.query_content:
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


class AugmentedReadingListTestCase(BaseReadingListTestCase):

    def setUp(self):
        super(AugmentedReadingListTestCase, self).setUp()
        # Fill up recent with more content
        make_content(TestReadingListObj, published=self.now, _quantity=50)
        self.another_campaign = Campaign.objects.create(
            sponsor_name="Fellas",
            start_date=self.now - timezone.timedelta(days=30),
            end_date=self.now + timezone.timedelta(days=30)
        )
        self.sponsored_content = make_content(
            TestReadingListObj,
            published=self.now - timezone.timedelta(hours=9),
            campaign=self.another_campaign,
            _quantity=20
        )
        Content.search_objects.refresh()

    def test_recent_augmented(self):
        example = Content.objects.last()
        self.assertEqual(example.reading_list_identifier, "recent")
        context = example.get_reading_list_context()
        self.assertEqual(context["name"], "Recent News")
        content = context["content"]
        res = [res for res in content]
        self.assertTrue(res[0].campaign)

    def test_section_augmented(self):
        self.add_section_identifiers()
        example = self.query_content[0]
        self.assertEqual(example.reading_list_identifier, self.section.es_id)
        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.section.name)
        content = context["content"]
        res = [res for res in content]
        self.assertTrue(res[0].campaign)

    def test_unsponsored_augmented(self):
        self.add_section_identifiers()
        self.add_unsponsored_special_coverage_identifiers()
        example = self.query_content[0]
        self.assertEqual(
            example.reading_list_identifier, self.unsponsored_special_coverage.identifier
        )
        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.unsponsored_special_coverage.name)
        content = context["content"]
        res = [res for res in content]
        self.assertTrue(res[0].campaign)

    def test_popular_augmented(self):
        self.add_section_identifiers()
        example = self.query_content[0]
        with mock.patch("pageview_client.clients.TrendingClient.get") as mock_get:
            mock_get.return_value = [obj.id for obj in self.query_content]
            self.assertEqual(example.reading_list_identifier, "popular")
            context = example.get_reading_list_context()
            self.assertEqual(context["name"], "popular")
            content = context["content"]
            res = [res for res in content]
            self.assertTrue(res[0].campaign)

    def test_sponsored_not_augmented(self):
        self.add_section_identifiers()
        self.add_unsponsored_special_coverage_identifiers()
        self.add_sponsored_special_coverage_identifiers()
        example = self.query_content[0]
        self.assertEqual(
            example.reading_list_identifier, self.sponsored_special_coverage.identifier
        )
        context = example.get_reading_list_context()
        self.assertEqual(context["name"], self.sponsored_special_coverage.name)
        content = context["content"]
        res = [res for res in content]
        self.assertFalse(res[0].campaign)