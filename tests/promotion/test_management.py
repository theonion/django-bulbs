from django.core.management.base import CommandError
from django.core import management

from bulbs.promotion.models import PZone
from bulbs.utils.test import BaseIndexableTestCase


class PZoneOperationsTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PZoneOperationsTestCase, self).setUp()

        self.pzone = PZone.objects.create(name="test-pzone", zone_length=10)

    def test_set_pzone_zone_length_valid(self):
        """Test that a valid call to this command succeeds."""

        new_length = self.pzone.zone_length + 5

        management.call_command(
            "set_pzone_zone_length",
            self.pzone.name,
            str(new_length))

        updated_pzone = PZone.objects.get(name="test-pzone")

        self.assertEqual(updated_pzone.zone_length, new_length)

    def test_set_pzone_length_invalid_name(self):
        """Test that an invalid pzone name given to this command fails."""

        with self.assertRaises(CommandError):
            management.call_command(
                "set_pzone_zone_length",
                "NOT-A-REAL-PZONE",
                "6")

    def test_set_pzone_length_invalid_zone_length(self):
        """Test that an invalid pzone zone_length given to this command fails."""

        new_length = -5

        with self.assertRaises(CommandError):
            management.call_command(
                "set_pzone_zone_length",
                "NOT-A-REAL-PZONE",
                str(new_length))
