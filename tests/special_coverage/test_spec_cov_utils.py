from django.test import override_settings
from django.utils import timezone

from bulbs.campaigns.models import Campaign
from bulbs.content.models import Content
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.special_coverage.utils import (
    get_sponsored_special_coverages, get_sponsored_special_coverage_query
)
from bulbs.utils.test import BaseIndexableTestCase, make_content


class SponsoredSpecialCoverageUtilsTestCase(BaseIndexableTestCase):
    def setUp(self, *arg, **kwargs):
        super(SponsoredSpecialCoverageUtilsTestCase, self).setUp()
        self.now = timezone.now()
        self.scheduled_content = make_content(
            published=self.now + timezone.timedelta(days=5),
            _quantity=12
        )
        self.recent_content = make_content(
            published=self.now - timezone.timedelta(hours=3),
            _quantity=12
        )
        self.not_so_recent_content = make_content(
            published=self.now - timezone.timedelta(days=3),
            _quantity=12
        )

        self.campaigns = (
            Campaign.objects.create(
                sponsor_name="Government",
                start_date=self.now - timezone.timedelta(days=5),
                end_date=self.now + timezone.timedelta(days=5)
            ),
            Campaign.objects.create(
                sponsor_name="MoneyDogs",
                start_date=self.now - timezone.timedelta(days=10),
                end_date=self.now + timezone.timedelta(days=10)
            ),
            Campaign.objects.create(
                sponsor_name="CashGuys",
                start_date=self.now + timezone.timedelta(days=10),
                end_date=self.now + timezone.timedelta(days=10)
            ),
        )
        self.special_coverages = (
            # Active Special Coverage, No Campaign.
            SpecialCoverage.objects.create(
                name="ello",
                start_date=self.now - timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=1),
                query={
                    "included_ids": [
                        self.scheduled_content[0].id,
                        self.scheduled_content[1].id,
                        self.recent_content[0].id,
                        self.recent_content[1].id,
                        self.not_so_recent_content[0].id,
                        self.not_so_recent_content[1].id
                    ]
                }
            ),
            # Active Special Coverage, Active Campaign
            SpecialCoverage.objects.create(
                name="guvna",
                campaign=self.campaigns[0],
                start_date=self.now - timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=1),
                query={
                    "included_ids": [
                        self.scheduled_content[2].id,
                        self.scheduled_content[3].id,
                        self.recent_content[2].id,
                        self.recent_content[3].id,
                        self.not_so_recent_content[2].id,
                        self.not_so_recent_content[3].id
                    ]
                }
            ),
            # Active Special Coverage, Active Campaign
            SpecialCoverage.objects.create(
                name="mawny",
                campaign=self.campaigns[1],
                start_date=self.now - timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=1),
                query={
                    "included_ids": [
                        self.scheduled_content[4].id,
                        self.scheduled_content[5].id,
                        self.recent_content[4].id,
                        self.recent_content[5].id,
                        self.not_so_recent_content[4].id,
                        self.not_so_recent_content[5].id
                    ]
                }
            ),
            # Inactive Special Coverage, Active Campaign
            SpecialCoverage.objects.create(
                name="mawnydogs",
                campaign=self.campaigns[1],
                start_date=self.now + timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=2),
                query={
                    "included_ids": [
                        self.scheduled_content[6].id,
                        self.scheduled_content[7].id,
                        self.recent_content[6].id,
                        self.recent_content[7].id,
                        self.not_so_recent_content[6].id,
                        self.not_so_recent_content[7].id
                    ]
                }
            ),
            # Active Special Coverage, Inactive Campaign
            SpecialCoverage.objects.create(
                name="cashyboys",
                campaign=self.campaigns[2],
                start_date=self.now - timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=1)
            ),
            # Inactive Special Coverage, Inactive Campaign
            SpecialCoverage.objects.create(
                name="nada",
                campaign=self.campaigns[2],
                start_date=self.now + timezone.timedelta(days=1),
                end_date=self.now + timezone.timedelta(days=3)
            )
        )
        Content.search_objects.refresh()

    def test_get_sponsored_special_coverages(self):
        """Should return 2 Special Coverage objects."""
        special_coverages = get_sponsored_special_coverages()
        self.assertEqual(special_coverages.count(), 2)
        self.assertIn(self.special_coverages[1], special_coverages)
        self.assertIn(self.special_coverages[2], special_coverages)

    def test_get_sponsored_special_coveage_query(self):
        """Should return all sponsored & published content."""
        query = get_sponsored_special_coverage_query()
        self.assertEqual(query.count(), 8)
        for obj in self.special_coverages[1].get_content():
            self.assertIn(obj, query)
        for obj in self.special_coverages[2].get_content():
            self.assertIn(obj, query)

    @override_settings(RECENT_SPONSORED_OFFSET=4)
    def test_get_sponsored_special_coverage_query_only_recent(self):
        """Should return all sponsored & published content."""
        query = get_sponsored_special_coverage_query(only_recent=True)
        self.assertEqual(query.count(), 4)
        for obj in self.special_coverages[1].get_content():
            if obj.published > self.now - timezone.timedelta(hours=4):
                self.assertIn(obj, query)
        for obj in self.special_coverages[2].get_content():
            if obj.published > self.now - timezone.timedelta(hours=4):
                self.assertIn(obj, query)
