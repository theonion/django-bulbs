from datetime import timedelta

from freezegun import freeze_time
from model_mommy import mommy

from django.utils import timezone

from bulbs.sections.models import Section
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase

from bulbs.content.models import Content, Tag

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def make_special_coverage(start=None, end=None, tag='test', included=None, sponsored=True):

    def days(count):
        return timezone.now() + timezone.timedelta(days=count)

    if start is not None and isinstance(start, int):
        start = days(start)
    if end is not None and isinstance(end, int):
        end = days(end)

    if sponsored:
        campaign = mommy.make("campaigns.Campaign", start_date=start, end_date=end)
    else:
        campaign = None

    return SpecialCoverage.objects.create(
        id=(SpecialCoverage.objects.count() + 1),  # Fixed ID ordering for easier asserts
        name="Test Coverage {}".format(SpecialCoverage.objects.count()),
        campaign=campaign,
        start_date=start,
        end_date=end,
        query={
            'excluded_ids': [],
            'groups': [{
                'conditions': [{
                    'field': 'tag',
                    'type': 'all',
                    'values': [{
                        'name': tag,
                        'value': tag,
                    }]
                }],
                'time': None
            }],
            'included_ids': [i.id for i in (included or [])],
            'pinned_ids': []
        }
    )


def make_section(tag='test'):
    section = Section.objects.create(
        id=(Section.objects.count() + 1),  # Fixed ID ordering for easier asserts
        name="Test Section {}".format(Section.objects.count()),
        query= {
            'groups': [{
                'conditions': [{
                    'field': 'tag',
                    'type': 'all',
                    'values': [{
                        'name': tag,
                        'value': tag,
                    }]
                }],
                'time': None
            }],
        })
    section._save_percolator()


class PercolateSpecialCoverageTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PercolateSpecialCoverageTestCase, self).setUp()
        self.content = Content.objects.create(
            id=1,
            title='A fun little article for the kids',
            published=timezone.now() - timezone.timedelta(days=500)
        )
        self.content.tags.add(Tag.objects.create(name='white', slug='white'))
        self.content.save()

        self.patch = patch('bulbs.content.models.logger')
        self.mock_logger = self.patch.start()

    def tearDown(self):
        self.patch.stop()
        # Ensure no errors or warnings
        self.assertFalse(self.mock_logger.error.call_args)
        self.assertFalse(self.mock_logger.warning.call_args)

    def check_special_coverages(self, expected_ids, sponsored_only=False):
        Content.search_objects.refresh()
        self.assertEqual(self.content.percolate_special_coverage(sponsored_only=sponsored_only),
                         ['specialcoverage.{}'.format(i) for i in expected_ids])

    def test_empty(self):
        self.check_special_coverages([], sponsored_only=True)
        self.check_special_coverages([], sponsored_only=False)

    def test_ignore_non_special_coverage(self):
        make_section(tag='white')
        self.check_special_coverages([], sponsored_only=True)
        self.check_special_coverages([], sponsored_only=False)

    def test_missing_dates(self):
        # Nothing will match, but need to ensure no ES errors from missing
        # "start_date/end_date" (via tearDown log check)
        make_special_coverage(tag='white')  # No dates
        self.check_special_coverages([], sponsored_only=True)
        self.check_special_coverages([], sponsored_only=False)

    def test_match_both_sponsored_and_unsponsored(self):
        make_special_coverage(tag='white', start=-3, end=1, sponsored=True)
        make_special_coverage(tag='white', start=-2, end=1, sponsored=False)
        make_special_coverage(tag='white', start=-1, end=1, sponsored=False)
        make_special_coverage(tag='white', start=0, end=1, sponsored=True)
        self.check_special_coverages([4, 1,   # Sponsored (sorted start date)
                                      3, 2])  # Unsponsored (sorted start date)

    def test_ignore_unsponsored(self):
        for sponsored in [True, False]:
            make_special_coverage(tag='white', start=-1, end=1, sponsored=sponsored)
        self.check_special_coverages([1], sponsored_only=True)

    def test_active_dates(self):

        with freeze_time('2016-02-07'):
            # Created 1 day before activation (2016-02-08)
            make_special_coverage(tag='white', start=1, end=2)
            # Inactive (1 day early)
            self.check_special_coverages([], sponsored_only=True)

        # Active
        with freeze_time('2016-02-08'):
            self.check_special_coverages([1], sponsored_only=True)

        # Inactive (1 day after)
        with freeze_time('2016-02-09'):
            self.check_special_coverages([], sponsored_only=True)

    def test_match_tag(self):
        make_special_coverage(tag='white', start=-1, end=1)
        make_special_coverage(tag='black', start=-1, end=1)
        self.check_special_coverages([1], sponsored_only=True)

    def test_prefer_manual(self):
        # Query match
        make_special_coverage(tag='white', start=-1, end=1),
        # Manually added (older but will be first)
        make_special_coverage(included=[self.content], start=-2, end=1),
        self.check_special_coverages([2, 1], sponsored_only=True)

    def test_sort_start_date(self):
        make_special_coverage(tag='white', start=-5, end=1)
        make_special_coverage(tag='white', start=-4, end=1)
        make_special_coverage(tag='white', start=-1, end=1)
        make_special_coverage(tag='white', start=-3, end=1)
        make_special_coverage(tag='white', start=-2, end=1)
        self.check_special_coverages([3, 5, 4, 2, 1], sponsored_only=True)

    def test_sort_start_date_same_day(self):
        # Percolator v1.4 scoring by date has ~1 hour accuracy (not sure why!)
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=4)), end=1)  # Oldest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=2)), end=1)  # 2nd Newest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=3)), end=1)  # 3rd Newest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=1)), end=1)  # Newest
        self.check_special_coverages([4, 2, 3, 1], sponsored_only=True)

    def test_precedence(self):
        # Manually added
        make_special_coverage(included=[self.content], start=-10, end=1)
        # Manually added but unsponsored
        make_special_coverage(included=[self.content], tag='white', start=-9, end=1, sponsored=False)
        # Manually added + tagged
        make_special_coverage(included=[self.content], tag='white', start=-5, end=1)
        # Query match
        make_special_coverage(tag='white', start=-10, end=1)
        make_special_coverage(tag='white', start=-9, end=1)
        make_special_coverage(tag='white', start=-8, end=1)
        # No match
        make_special_coverage(tag='black', start=-10, end=1)
        # Inactive
        make_special_coverage(tag='black', start=-10, end=0)
        make_special_coverage(tag='black', start=1, end=20)
        # Active, but not sponsored
        make_special_coverage(tag='white', start=-50, end=1, sponsored=False)

        # Within each group, sorted by start date
        self.check_special_coverages([3, 1,      # Sponsored manually added
                                      6, 5, 4],  # Sponsored query included
                                     sponsored_only=True)
        self.check_special_coverages([3, 1,     # Sponsored manually added
                                      6, 5, 4,  # Sponsored query included
                                      2,        # Not Sponsored manually added
                                      10],      # Not Sponsored query included
                                     sponsored_only=False)
