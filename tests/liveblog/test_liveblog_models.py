from freezegun import freeze_time
import six
from mock import call, patch

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
    def test_save_signal(self):

        liveblog = TestLiveBlog.objects.create()

        with patch('bulbs.liveblog.signals.firebase_update_entry.delay') as mock_task:
            # Create
            entry = LiveBlogEntry.objects.create(liveblog=liveblog)
            self.assertEqual(1, mock_task.call_count)

            # Update
            entry.save()
            self.assertEqual(2, mock_task.call_count)

            # Called 2 times with liveblog ID
            mock_task.assert_has_calls([call(entry.id) for _ in range(2)])

    def test_delete_signal(self):

        liveblog = TestLiveBlog.objects.create()
        entry = LiveBlogEntry.objects.create(liveblog=liveblog)

        with patch('bulbs.liveblog.signals.firebase_delete_entry.delay') as mock_task:

            entry_id = entry.id
            entry.delete()
            mock_task.assert_called_once_with(entry_id)
