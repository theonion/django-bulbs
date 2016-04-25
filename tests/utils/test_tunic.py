import requests_mock

from django.test import override_settings, TestCase

from bulbs.utils.tunic import TunicClient, RequestFailure


@override_settings(TUNIC_BACKEND_ROOT='http://onion.local/api/v1/',
                   TUNIC_REQUEST_TOKEN='12345')
class GetActiveCampaignsTests(TestCase):

    def test_get_active_campaigns(self):
        with requests_mock.mock() as mocker:
            mocker.get('http://onion.local/api/v1/campaign/?active=true',
                       status_code=200,
                       json={'results': [{'id': 1,
                                          'name': 'My Campaign'},
                                         {'id': 2,
                                          'name': 'Another Campaign'}]},
                       headers={'Authorizaton': 'Token 12345'})
            self.assertEqual(TunicClient().get_active_campaigns(),
                             {1: {'id': 1,
                                  'name': 'My Campaign'},
                              2: {'id': 2,
                                  'name': 'Another Campaign'}})

    def test_connection_error(self):
        with self.assertRaises(RequestFailure):
            with requests_mock.mock() as mocker:
                mocker.get('http://onion.local/api/v1/campaign/?active=true',
                           status_code=500,
                           headers={'Authorizaton': 'Token 12345'})
                TunicClient().get_active_campaigns()
