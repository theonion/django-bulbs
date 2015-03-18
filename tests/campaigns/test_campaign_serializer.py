from django.test import TestCase

from bulbs.campaigns.models import CampaignPixel
from bulbs.campaigns.serializers import PixelTypeField


class PixelTypeFieldCase(TestCase):

    def test_from_native(self):
        field = PixelTypeField()
        self.assertEqual(CampaignPixel.LOGO, field.from_native('Logo'))
        with self.assertRaises(KeyError):
            field.from_native(None)

    def test_to_native(self):
        field = PixelTypeField()
        self.assertEqual('Logo', field.to_native(CampaignPixel.LOGO))
        with self.assertRaises(KeyError):
            field.to_native(None)
