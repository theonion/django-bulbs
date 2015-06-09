from django.test import TestCase

from bulbs.campaigns.models import CampaignPixel


class PixelTypeFieldCase(TestCase):

    def test_from_native(self):
        # TODO: top-level import causes Travis test to fail
        from bulbs.campaigns.serializers import PixelTypeField
        field = PixelTypeField()
        self.assertEqual(CampaignPixel.LISTING, field.to_internal_value('Listing'))
        with self.assertRaises(KeyError):
            field.to_internal_value(None)

    def test_to_native(self):
        # TODO: top-level import causes Travis test to fail
        from bulbs.campaigns.serializers import PixelTypeField
        field = PixelTypeField()
        self.assertEqual('Listing', field.to_representation(CampaignPixel.LISTING))
        with self.assertRaises(KeyError):
            field.to_representation(None)
