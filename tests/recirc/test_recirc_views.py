from django.core.urlresolvers import reverse

from bulbs.utils.test import BaseAPITestCase


class TestRecircViews(BaseAPITestCase):

    def setUp(self):
        super(TestRecircViews, self).setUp()

    def test_recirc_url(self):
        # create dumb test objects

        # call endpoint
        recirc_url = reverse('content_recirc', kwargs={'pk': 1})
        response = self.api_client.get(recirc_url)
        self.assertEqual(response.status_code, 200)

        # assert first three things are returned from dumb endpoint

    def test_recirc_content_not_found(self):
        pass

    def test_recirc_unpublished(self):
        pass
