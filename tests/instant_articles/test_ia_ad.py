from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test.client import Client
from django.test.utils import override_settings

from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


DFP_SITE = "www.google.com"


class InstantArticleAdViewTests(BaseIndexableTestCase):
    def setUp(self):
        super(InstantArticleAdViewTests, self).setUp()
        self.client = Client()
        self.feature_type = FeatureType.objects.create(name="AdBoys", instant_article=True)
        self.content = make_content(TestContentObj, feature_type=self.feature_type)
        self.url = reverse("instant_article_ad", kwargs={"pk": self.content.pk})

        User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    @override_settings(DFP_SITE=DFP_SITE)
    def test_ad_unit(self):
        self.client.login(username="admin", password="secret")

        response = self.client.get(self.url)
        targeting = response.context_data.get("targeting")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.feature_type.slug, targeting.get("dfp_feature"))
        self.assertEqual(DFP_SITE, targeting.get("dfp_site"))
        self.assertEqual(self.content.id, targeting.get("dfp_contentid"))
        self.assertEqual(self.content.__class__.__name__.lower(), targeting.get("dfp_pagetype"))
        self.assertEqual(self.content.slug, targeting.get("dfp_slug"))
