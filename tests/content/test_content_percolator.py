from datetime import timedelta

from freezegun import freeze_time
from model_mommy import mommy
import six

from django.utils import timezone

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase

from bulbs.content.models import Content, Tag


def make_special_coverage(start, end, tag='test', included=None, sponsored=True):

    def days(count):
        return timezone.now() + timezone.timedelta(days=count)

    if isinstance(start, int):
        start = days(start)
    if isinstance(end, int):
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
            # 'included_ids': [local_article.id] + [a.id for a in sponsored_articles],
            'included_ids': [i.id for i in (included or [])],
            'pinned_ids': []
        }
    )


class PercolateSpecialCoveragesTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PercolateSpecialCoveragesTestCase, self).setUp()
        self.content = Content.objects.create(
            id=1,
            title='A fun little article for the kids',
            published=timezone.now() - timezone.timedelta(days=500)
        )
        self.content.tags.add(Tag.objects.create(name='white', slug='white'))
        self.content.save()

    def check_special_coverages(self, expected_ids):
        Content.search_objects.refresh()
        # Unordered results
        six.assertCountEqual(self, self.content.percolate_special_coverages(),
                             ['specialcoverage.{}'.format(i) for i in expected_ids])

    def test_empty(self):
        self.check_special_coverages([])

    def test_match_manual(self):
        make_special_coverage(included=[self.content], start=-1, end=1),
        make_special_coverage(tag='white', included=[self.content], start=-1, end=1),
        self.check_special_coverages([1, 2])  # Both match

    def test_match_tag(self):
        make_special_coverage(tag='white', start=-1, end=1)
        make_special_coverage(tag='black', start=-1, end=1)
        self.check_special_coverages([1])  # Only 'white' tag match

    def test_match_both_sponsored_and_unsponsored(self):
        make_special_coverage(tag='white', start=-1, end=1, sponsored=True)
        make_special_coverage(tag='white', start=-1, end=1, sponsored=False)
        self.check_special_coverages([1, 2])  # Both match


class PercolateSponsoredSpecialCoveragesTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PercolateSponsoredSpecialCoveragesTestCase, self).setUp()
        self.content = Content.objects.create(
            id=1,
            title='A fun little article for the kids',
            published=timezone.now() - timezone.timedelta(days=500)
        )
        self.content.tags.add(Tag.objects.create(name='white', slug='white'))
        self.content.save()

    def check_special_coverages(self, expected_ids):
        Content.search_objects.refresh()
        self.assertEqual(self.content.percolate_sponsored_special_coverages(),
                         ['specialcoverage.{}'.format(i) for i in expected_ids])

    def test_empty(self):
        self.check_special_coverages([])

    def test_ignore_unsponsored(self):
        for sponsored in [True, False]:
            make_special_coverage(tag='white', start=-1, end=1, sponsored=sponsored)
        self.check_special_coverages([1])

    def test_active_dates(self):

        with freeze_time('2016-02-07'):
            # Created 1 days before activation (2016-02-08)
            make_special_coverage(tag='white', start=1, end=2)
            # Inactive (1 day early)
            self.check_special_coverages([])

        # Active
        with freeze_time('2016-02-08'):
            self.check_special_coverages([1])

        # Inactive (1 day after)
        with freeze_time('2016-02-09'):
            self.check_special_coverages([])

    def test_match_tag(self):
        make_special_coverage(tag='white', start=-1, end=1)
        make_special_coverage(tag='black', start=-1, end=1)
        self.check_special_coverages([1])

    def test_prefer_manual(self):
        # Query match
        make_special_coverage(tag='white', start=-1, end=1),
        # Manually added (older but will be first)
        make_special_coverage(included=[self.content], start=-2, end=1),
        self.check_special_coverages([2, 1])

    def test_sort_start_date(self):
        make_special_coverage(tag='white', start=-5, end=1)
        make_special_coverage(tag='white', start=-4, end=1)
        make_special_coverage(tag='white', start=-1, end=1)
        make_special_coverage(tag='white', start=-3, end=1)
        make_special_coverage(tag='white', start=-2, end=1)
        self.check_special_coverages([3, 5, 4, 2, 1])

    def test_sort_start_date_same_day(self):
        # Percolator v1.4 scoring by date has ~1 hour accuracy (not sure why!)
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=4)), end=1)  # Oldest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=2)), end=1)  # 2nd Newest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=3)), end=1)  # 3rd Newest
        make_special_coverage(tag='white', start=(timezone.now() - timedelta(hours=1)), end=1)  # Newest
        self.check_special_coverages([4, 2, 3, 1])

    def test_precedence(self):
        # Manually added
        make_special_coverage(included=[self.content], start=-10, end=1)
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
        # Not sponsored
        make_special_coverage(tag='white', start=-10, end=1, sponsored=False)

        self.check_special_coverages([2, 1,      # Manually added (sorted start date)
                                      5, 4, 3])  # Query included (sorted start date)
