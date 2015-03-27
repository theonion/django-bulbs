from datetime import datetime
import json

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
            "sponsor_logo": {'id': 123},
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date": END_DATE.isoformat(),
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
                          "sponsor_logo": {'id': 123},
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date": END_DATE,
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
            "sponsor_logo": {'id': 123},
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date": END_DATE.isoformat(),
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
                          "sponsor_logo": {'id': 123},
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date": END_DATE,
                          "pixels": [{"id": pixel.id,
                                      "url": "http://example.com/pixel/1",
                                      "pixel_type": "Logo"}],
                          },
                         response.data)

    def test_update_campaign_delete_pixel(self):
        campaign = Campaign.objects.create(sponsor_name="Original Name",
                                           campaign_label="Original Label")
        CampaignPixel.objects.create(url="http://example.com/pixel/1",
                                     campaign=campaign,
                                     pixel_type=CampaignPixel.LOGO)

        data = {
            "id": campaign.id,
            "sponsor_name": "Acme",
            "sponsor_logo": {'id': 123},
            "sponsor_url": "http://example.com",
            "start_date": START_DATE.isoformat(),
            "end_date": END_DATE.isoformat(),
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
                          "sponsor_logo": {'id': 123},
                          "sponsor_url": "http://example.com",
                          "campaign_label": "Test Label",
                          "impression_goal": 1000,
                          "start_date": START_DATE,
                          "end_date": END_DATE,
                          "pixels": [],
                          },
                         response.data)

    def test_search_campaign_by_campaign(self):
        """Test that searching campaigns by their label works."""

        # matching campaign
        campaign_label = "O-1337 Honda"
        campaign = Campaign.objects.create(sponsor_name="Original Name",
                                           campaign_label=campaign_label)

        # non-matching campaign
        Campaign.objects.create(sponsor_name="Original Name",
                                campaign_label="NO!")

        client = Client()
        client.login(username="admin", password="secret")
        campaign_list_endpoint = reverse("campaign-list")
        response = client.get(campaign_list_endpoint, data={"search": campaign_label})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], campaign.pk)

    def test_search_campaign_by_sponsor(self):
        """Test that searching campaigns by their sponsor name works."""

        # matching campaign
        sponsor_name = "Hondaz"
        campaign = Campaign.objects.create(sponsor_name=sponsor_name,
                                           campaign_label="O-1337 HONADZ")

        # non-matching campaign
        Campaign.objects.create(sponsor_name="Hagendaz",
                                campaign_label="O-1SCRM Hagendaz")

        client = Client()
        client.login(username="admin", password="secret")
        campaign_list_endpoint = reverse("campaign-list")
        response = client.get(campaign_list_endpoint, data={"search": sponsor_name})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], campaign.pk)

    def test_search_campaign_ordering(self):
        """Test that campaign search results are ordered."""

        campaign_3 = Campaign.objects.create(sponsor_name="abc3",
                                             campaign_label="abc3")
        campaign_1 = Campaign.objects.create(sponsor_name="abc1",
                                             campaign_label="abc1")
        campaign_2 = Campaign.objects.create(sponsor_name="abc2",
                                             campaign_label="abc2")

        client = Client()
        client.login(username="admin", password="secret")
        campaign_list_endpoint = reverse("campaign-list")
        response = client.get(campaign_list_endpoint,
                              data={"search": "abc", "ordering": "-campaign_label"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], campaign_3.pk)
        self.assertEqual(response.data["results"][1]["id"], campaign_2.pk)
        self.assertEqual(response.data["results"][2]["id"], campaign_1.pk)
