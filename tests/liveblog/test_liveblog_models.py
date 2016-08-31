from freezegun import freeze_time
import requests_mock
import six

from django.test.utils import override_settings

from bulbs.utils.test import BaseIndexableTestCase, make_content
from bulbs.liveblog.models import LiveBlogEntry

from example.testcontent.models import TestLiveBlog


class TestLiveBlogModel(BaseIndexableTestCase):

    def test_pinned_content(self):
        content = make_content()
        liveblog = TestLiveBlog.objects.create(pinned_content=content)
        self.assertEqual(liveblog.pinned_content, content)
        self.assertEqual(liveblog, content.liveblog_pinned.first())

    def test_recirc_content(self):
        content = make_content(_quantity=3)

        liveblog = TestLiveBlog.objects.create()
        liveblog.recirc_content.add(*content)
        liveblog.save()

        six.assertCountEqual(self, liveblog.recirc_content.all(), content)
        self.assertEqual(liveblog, content[0].liveblog_recirc.first())


class TestLiveBlogEntryModel(BaseIndexableTestCase):

    @freeze_time('2016-08-31 12:13:14')
    @override_settings(LIVEBLOG_FIREBASE_NOTIFY_ENDPOINT='http://firebase.local/{liveblog_id}.json')
    def test_save_signal(self):

        liveblog = TestLiveBlog.objects.create()

        with requests_mock.mock() as mocker:
            mocker.put('http://firebase.local/{}.json'.format(liveblog.id),
                       status_code=200)

            # Create
            entry = LiveBlogEntry.objects.create(liveblog=liveblog)
            self.assertEqual(mocker.call_count, 1)

            # Update
            entry.save()
            self.assertEqual(mocker.call_count, 2)

            # Delete
            entry.delete()
            self.assertEqual(mocker.call_count, 3)

            # Verify all request arguments
            for req in mocker.request_history:
                self.assertEqual(req.json(), {'updatedAt': 1472645594.0})
