import requests_mock

from django.test import override_settings, TestCase

from bulbs.utils.tunic import TunicClient, RequestFailure


@override_settings(TUNIC_STAFF_BACKEND_ROOT='http://onion.local/',
                   TUNIC_API_PATH="/api/v1/",
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

    def test_get_all_paginated_campaigns(self):
        with requests_mock.mock() as mocker:
            page1 = "http://onion.local/api/v1/campaign/?active=true"
            page2 = "http://onion.local/api/v1/campaign/?page=2&active=true"
            mocker.get(page1,
                       status_code=200,
                       json={'next': page2,
                             'results': [{'id': 1,
                                          'name': 'My Campaign'},
                                         {'id': 2,
                                          'name': 'Another Campaign'}]},
                       headers={'Authorizaton': 'Token 12345'})
            mocker.get(page2,
                       status_code=200,
                       json={'results': [{'id': 3,
                                          'name': 'More Campaign'},
                                         {'id': 4,
                                          'name': 'Enough with the campaigns already!'}]},
                       headers={'Authorizaton': 'Token 12345'})
            self.assertEqual(TunicClient().get_active_campaigns(),
                             {1: {'id': 1,
                                  'name': 'My Campaign'},
                              2: {'id': 2,
                                  'name': 'Another Campaign'},
                              3: {'id': 3,
                                  'name': 'More Campaign'},
                              4: {'id': 4,
                                  'name': 'Enough with the campaigns already!'}})

    def test_get_weighted_campaigns(self):
        with requests_mock.mock() as mocker:
            mocker.get('http://onion.local/api/v1/campaign/?weighted=true',
                       status_code=200,
                       json={'results': [{'id': 1,
                                          'name': 'My Campaign'}]},
                       headers={'Authorizaton': 'Token 12345'})
            self.assertEqual(TunicClient().get_campaigns(filter_weighted=True),
                             {1: {'id': 1,
                                  'name': 'My Campaign'}})

    def test_backend_error(self):
        with self.assertRaises(RequestFailure):
            with requests_mock.mock() as mocker:
                mocker.get('http://onion.local/api/v1/campaign/?active=true',
                           status_code=500,
                           headers={'Authorizaton': 'Token 12345'})
                TunicClient().get_active_campaigns()
