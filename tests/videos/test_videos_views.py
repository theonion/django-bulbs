from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase, make_content
from bulbs.campaigns.models import Campaign
from bulbs.special_coverage.models import SpecialCoverage


class TestVideosViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestVideosViews, self).setUp()
        self.client = Client()
