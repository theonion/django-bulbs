"""Tests for bulbs.contributions.email."""
import random

from django.contrib.auth import get_user_model
from django.utils import timezone

from bulbs.contributions.email import EmailReport
from bulbs.contributions.models import ContributorRole
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


User = get_user_model()  # NOQA


class EmailReportTestCase(BaseIndexableTestCase):
    """TestCase for bulbs.contributions.email.EmailReport."""

    def setUp(self):  # NOQA
        super(EmailReportTestCase, self).setUp()
        # Define relevant variables.
        self.last_month = (self.now.month - 1) % 12
        self.next_month = (self.now.month + 1) % 12

        # Add Users.
        self.tony_sarpino = User.objects.create(
            first_name="Tony", last_name="Sarpino", username="Tone"
        )
        self.buddy_sarpino = User.objects.create(
            first_name="Buddy", last_name="Sarpino", username="Buddy"
        )

        # Add Roles.
        self.draft_writer = ContributorRole.objects.create(name="Draft Writer", payment_type=0)

        # Add Rates.
        self.draft_writer.flat_rates.create(rate=60)

        # Make Content with contributions.
        make_content(
            TestContentObj,
            authors=[self.tony_sarpino],
            published=timezone.datetime(
                day=random.randrange(1, 28), month=self.now.month, year=self.now.year
            ),
            _quantity=25
        )
        make_content(
            TestContentObj,
            authors=[self.tony_sarpino, self.buddy_sarpino],
            published=timezone.datetime(
                day=random.randrange(1, 28), month=self.last_month, year=self.now.year
            ),
            _quantity=25
        )
        make_content(
            TestContentObj,
            authors=[self.tony_sarpino],
            published=timezone.datetime(
                day=random.randrange(1, 28), month=self.next_month, year=self.now.year
            ),
            _quantity=25
        )

        # Refresh the index.
        TestContentObj.search_objects.refresh()

    def test_get_contributors_default(self):  # NOQA
        report = EmailReport()
        contributors = report.get_contributors()
        self.assertEqual(contributors.count(), 1)

    def test_get_contributors_last_month(self):  # NOQA
        report = EmailReport(month=self.last_month)
        contributors = report.get_contributors()
        self.assertEqual(contributors.count(), 2)

    def test_get_contributor_contributions_default(self):  # NOQA
        report = EmailReport()
        contributions = report.get_contributions_by_contributor(self.tony_sarpino)
        self.assertEqual(contributions.count(), 25)

    def test_get_contributor_contributions_next_month(self):  # NOQA
        report = EmailReport(month=self.next_month)
        contributions = report.get_contributions_by_contributor(self.tony_sarpino)
        self.assertEqual(contributions.count(), 25)
