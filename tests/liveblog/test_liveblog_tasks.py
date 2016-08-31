from freezegun import freeze_time
from requests.exceptions import HTTPError
import requests_mock

from django.test import TestCase
from django.test.utils import override_settings

from bulbs.liveblog.tasks import firebase_update_timestamp


@override_settings(LIVEBLOG_FIREBASE_NOTIFY_ENDPOINT='http://firebase.local/{liveblog_id}.json')
class TestFiresbaseUpdateTimestamp(TestCase):

    @freeze_time('2016-08-31 12:13:14')
    def test_success(self):
        with requests_mock.mock() as mocker:
            mocker.put('http://firebase.local/123.json', status_code=200)

            firebase_update_timestamp(123)

            self.assertEqual(mocker.call_count, 1)
            self.assertEqual(mocker.request_history[0].json(),
                             {'updatedAt': 1472645594.0})

    def test_request_error(self):
        with requests_mock.mock() as mocker:
            mocker.put('http://firebase.local/123.json', status_code=500)

            with self.assertRaises(HTTPError):
                firebase_update_timestamp(123)
