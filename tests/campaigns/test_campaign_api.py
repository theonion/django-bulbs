from datetime import datetime
import json
import unittest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from bulbs.campaigns.models import Campaign, CampaignPixel


START_DATE = datetime(2015, 3, 19, 19, 0, 5)
END_DATE = datetime(2015, 3, 20, 20, 0, 5)


class CampaignApiCase(TestCase):

    def setUp(self):
        User = get_user_model()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_get_api(self):
        campaign = Campaign.objects.create(sponsor_name="Sponsor",
                                           campaign_label="Label")
        pixel = CampaignPixel.objects.create(url="http://example.com/1",
                                             campaign=campaign,
                                             pixel_type=CampaignPixel.LOGO)
        client = Client()
        client.login(username="admin", password="secret")
        campaign_detail_endpoint = reverse("campaign-detail", kwargs=dict(pk=campaign.pk))
        response = client.get(campaign_detail_endpoint, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(data["id"], campaign.id)
        self.assertEqual(len(data["pixels"]), 1)
        self.assertEqual(data["pixels"][0],
                         {"id": pixel.id,
                          "url": "http://example.com/1",
                          "pixel_type": "Logo"},
                         )

    def test_create_campaign(self):
        data = {
            "sponsor_name": "Acme",
            #"sponsor_logo": TODO
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date":  END_DATE.isoformat(),
            "campaign_label": "Test Label",
            "impression_goal": 1000,
            "pixels": [{"url": "http://example.com/pixel/1",
                        "pixel_type": "Logo"}],
        }
        client = Client()
        client.login(username="admin", password="secret")
        campaign_detail_endpoint = reverse("campaign-list")
        response = client.post(campaign_detail_endpoint, json.dumps(data),
                               content_type="application/json")
        self.assertEqual(response.status_code, 201)  # 201 Created

        # assert that we can load it up
        campaign = Campaign.objects.get(id=response.data["id"])
        self.assertEqual(campaign.sponsor_name, data["sponsor_name"])
        self.assertEqual(1, campaign.pixels.count())
        pixel = campaign.pixels.first()
        self.assertEqual(pixel.url, data["pixels"][0]["url"])

        # check that all the fields went through
        self.assertEqual({"id": campaign.id,
                          "sponsor_name": "Acme",
                          "sponsor_logo": None,  # TODO
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date":  END_DATE,
                          "pixels": [{"id": pixel.id,
                                      "url": "http://example.com/pixel/1",
                                      "pixel_type": "Logo"}],
                          },
                         response.data)

    def test_update_campaign(self):
        campaign = Campaign.objects.create(sponsor_name="Original Name",
                                           campaign_label="Original Label")

        data = {
            "id": campaign.id,
            "sponsor_name": "Acme",
            #"sponsor_logo": TODO
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date":  END_DATE.isoformat(),
            "campaign_label": "Test Label",
            "impression_goal": 1000,
            "pixels": [{"url": "http://example.com/pixel/1",
                        "pixel_type": "Logo"}],
        }

        client = Client()
        client.login(username="admin", password="secret")
        campaign_detail_endpoint = reverse("campaign-detail", kwargs=dict(pk=campaign.pk))
        response = client.put(campaign_detail_endpoint, json.dumps(data),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # assert model updated
        campaign = Campaign.objects.get(id=response.data["id"])
        self.assertEqual(campaign.sponsor_name, data["sponsor_name"])
        self.assertEqual(1, campaign.pixels.count())
        pixel = campaign.pixels.first()
        self.assertEqual(pixel.url, data["pixels"][0]["url"])

        # check that all the fields went through
        self.assertEqual({"id": campaign.id,
                          "sponsor_name": "Acme",
                          "sponsor_logo": None,  # TODO
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date":  END_DATE,
                          "pixels": [{"id": pixel.id,
                                      "url": "http://example.com/pixel/1",
                                      "pixel_type": "Logo"}],
                          },
                         response.data)

    def test_update_campaign_delete_pixel(self):
        campaign = Campaign.objects.create(sponsor_name="Original Name",
                                           campaign_label="Original Label")
        pixel = CampaignPixel.objects.create(url="http://example.com/pixel/1",
                                             campaign=campaign,
                                             pixel_type=CampaignPixel.LOGO)

        data = {
            "id": campaign.id,
            "sponsor_name": "Acme",
            #"sponsor_logo": TODO
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date":  END_DATE.isoformat(),
            "campaign_label": "Test Label",
            "impression_goal": 1000,
            "pixels": [],
        }

        client = Client()
        client.login(username="admin", password="secret")
        campaign_detail_endpoint = reverse("campaign-detail", kwargs=dict(pk=campaign.pk))
        response = client.put(campaign_detail_endpoint, json.dumps(data),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # assert model updated
        campaign = Campaign.objects.get(id=response.data["id"])
        self.assertEqual(0, campaign.pixels.count())

        # check that all the fields went through
        self.assertEqual({"id": campaign.id,
                          "sponsor_name": "Acme",
                          "sponsor_logo": None,  # TODO
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date":  END_DATE,
                          "pixels": [],
                          },
                         response.data)
