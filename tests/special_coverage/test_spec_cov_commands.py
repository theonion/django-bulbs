from django.core.management import call_command

from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseIndexableTestCase


class SpecialCoverageCommandTests(BaseIndexableTestCase):

    def setUp(self):
        super(SpecialCoverageCommandTests, self).setUp()
        for i in range(50):
            SpecialCoverage.objects.create(name="sc{}".format(i), active=True)
            SpecialCoverage.objects.create(name="inactive-sc{}".format(i))

    def test_active_migration_success(self):
        call_command("migrate_active_to_published")
        start_qs = SpecialCoverage.objects.filter(start_date__isnull=False)
        self.assertEqual(start_qs.count(), 50)
        end_qs = SpecialCoverage.objects.filter(end_date__isnull=False)
        self.assertEqual(end_qs.count(), 50)

        inactive_qs = SpecialCoverage.objects.filter(
            start_date__isnull=True, end_date__isnull=True
        )
        self.assertEqual(inactive_qs.count(), 50)
        for sc in inactive_qs:
            self.assertNotIn(sc, start_qs)
            self.assertNotIn(sc, end_qs)
