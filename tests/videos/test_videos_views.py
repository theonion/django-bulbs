from django.test import Client
from django.core.urlresolvers import reverse

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.utils.test.make_vcr import make_vcr


vcr = make_vcr(__file__)


class TestVideosViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestVideosViews, self).setUp()
        self.client = Client()

    @vcr.use_cassette()
    def test_series_detail_view(self):
        response = self.client.get(reverse("series_detail", kwargs={"slug": "talent-show"}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['series_name'], 'Talent Show')
        self.assertEqual(response.context['channel_name'], 'The A.V. Club')
        self.assertEqual(response.context['series_description'], '')
        self.assertEqual(response.context['total_seasons'], 0)
        self.assertEqual(response.context['total_episodes'], 9)

    @vcr.use_cassette()
    def test_series_detail_view_not_found(self):
        response = self.client.get(reverse("series_detail", kwargs={"slug": "non-existant-show"}))
        self.assertEqual(response.status_code, 404)
