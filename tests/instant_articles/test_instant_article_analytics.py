from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings

from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


DFP_SITE = "www.google.com"


class AnalyticsViewTests(BaseIndexableTestCase):

    def setUp(self):
        super(AnalyticsViewTests, self).setUp()
        self.feature_type = FeatureType.objects.create(
            name="Ey go that way bruh", instant_article=True
        )
        self.content = make_content(TestContentObj, feature_type=self.feature_type)
        User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    @override_settings(DFP_SITE=DFP_SITE)
    def test_analytics(self):
        self.client = Client()
        self.client.login(username="admin", password="secret")
        url = reverse("instant_article_analytics", kwargs={"pk": self.content.pk})

        response = self.client.get(url)
        targeting = response.context_data.get("targeting")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("Instant Articles", response.context_data.get("platform"))
        self.assertEqual(DFP_SITE, targeting.get("dfp_site"))
        self.assertEqual(self.feature_type.slug, targeting.get("dfp_feature"))
        self.assertEqual(self.content.id, targeting.get("dfp_contentid"))
        self.assertEqual(self.content.__class__.__name__.lower(), targeting.get("dfp_pagetype"))
        self.assertEqual(self.content.slug, targeting.get("dfp_slug"))
        self.assertTrue(targeting.get("dfp_instant_article"))
