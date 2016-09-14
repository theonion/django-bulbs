import factory
from requests.exceptions import HTTPError
import requests_mock

from django.db.models import signals as signals
from django.utils import timezone
from django.test import TestCase
from django.test.utils import override_settings

from bulbs.liveblog.models import LiveBlogEntry
from bulbs.liveblog.tasks import firebase_delete_entry, firebase_update_entry

from example.testcontent.models import TestLiveBlog


TEST_ENDPOINT = 'http://firebase.local/{liveblog_id}/{entry_id}.json'


@override_settings(LIVEBLOG_FIREBASE_NOTIFY_ENDPOINT=TEST_ENDPOINT)
class BaseFirebaseTaskTestCase(TestCase):

    @factory.django.mute_signals(signals.post_save)  # Disable triggering method under test
    def setUp(self):
        super(BaseFirebaseTaskTestCase, self).setUp()
        liveblog = TestLiveBlog.objects.create()
        self.entry = LiveBlogEntry.objects.create(liveblog=liveblog)
        self.url = TEST_ENDPOINT.format(liveblog_id=self.entry.liveblog.id,
                                        entry_id=self.entry.id)


class TestFirebaseUpdateEntry(BaseFirebaseTaskTestCase):

    def test_update_published(self):

        now = timezone.now()

        with factory.django.mute_signals(signals.post_save):  # Disable triggering method under test
            self.entry.published = now
            self.entry.save()

        with requests_mock.mock() as mocker:
            mocker.patch(self.url, status_code=200)

            firebase_update_entry(self.entry.id)

            self.assertEqual(mocker.call_count, 1)
            self.assertEqual(mocker.request_history[0].json(),
                             {'published': now.isoformat()})

    def test_update_unpublished(self):

        with requests_mock.mock() as mocker:
            mocker.delete(self.url, status_code=200)

            firebase_update_entry(self.entry.id)

            self.assertEqual(mocker.call_count, 1)

    def test_request_error(self):

        with requests_mock.mock() as mocker:
            mocker.delete(self.url, status_code=500)

            with self.assertRaises(HTTPError):
                firebase_update_entry(self.entry.id)


class TestFirebaseDeleteEntry(BaseFirebaseTaskTestCase):

    def test_delete(self):

        with requests_mock.mock() as mocker:
            mocker.delete(self.url, status_code=200)

            firebase_delete_entry(self.entry.id)

            self.assertEqual(mocker.call_count, 1)

    def test_request_error(self):

        with requests_mock.mock() as mocker:
            mocker.delete(self.url, status_code=500)

            with self.assertRaises(HTTPError):
                firebase_delete_entry(self.entry.id)
