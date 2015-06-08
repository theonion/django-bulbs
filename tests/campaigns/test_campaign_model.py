from django.test import TestCase

from bulbs.campaigns.models import Campaign, CampaignPixel
from bulbs.utils.test import BaseIndexableTestCase


class CampaignModelCase(BaseIndexableTestCase):

    def test_model(self):
        campaign = Campaign.objects.create(sponsor_name='Sponsor',
                                           campaign_label='Label')
        self.assertIsNotNone(campaign.id)
