from django.test import TestCase

from bulbs.campaigns.models import CampaignPixel


class PixelTypeFieldCase(TestCase):

    def test_from_native(self):
        # TODO: top-level import causes Travis test to fail
        from bulbs.campaigns.serializers import PixelTypeField
        field = PixelTypeField()
        self.assertEqual(CampaignPixel.LOGO, field.to_internal_value('Logo'))
        with self.assertRaises(KeyError):
            field.to_internal_value(None)

    def test_to_native(self):
        # TODO: top-level import causes Travis test to fail
        from bulbs.campaigns.serializers import PixelTypeField
        field = PixelTypeField()
        self.assertEqual('Logo', field.to_representation(CampaignPixel.LOGO))
        with self.assertRaises(KeyError):
            field.to_representation(None)
