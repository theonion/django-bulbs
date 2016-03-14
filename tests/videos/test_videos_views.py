from django.core.urlresolvers import reverse
from django.test import Client

from bulbs.utils.test import BaseIndexableTestCase


class TestVideosViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestVideosViews, self).setUp()
        self.client = Client()
