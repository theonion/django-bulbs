import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from bulbs.campaigns.models import Campaign, CampaignPixel


class CampaignApiCase(TestCase):

    def setUp(self):
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_api(self):
        campaign = Campaign.objects.create(sponsor_name="Sponsor",
                                           campaign_label="Label")
        pixel = CampaignPixel.objects.create(url='http://example.com/1',
                                             campaign=campaign,
                                             campaign_type=CampaignPixel.LOGO)
        client = Client()
        client.login(username="admin", password="secret")
        campaign_detail_endpoint = reverse("campaign-detail", kwargs=dict(pk=campaign.pk))
        response = client.get(campaign_detail_endpoint, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(data['id'], campaign.id)
        self.assertEqual(len(data['pixels']), 1)
        self.assertEqual(data['pixels'][0],
                         {'id': pixel.id,
                          'url': 'http://example.com/1',
                          'campaign_type': 'Logo'},
                         )
