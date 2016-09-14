from datetime import datetime, timedelta

from django.test.client import RequestFactory
from django.http import Http404

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.liveblog.views import LiveblogNewEntriesView
from bulbs.liveblog.models import LiveBlogEntry

from example.testcontent.models import TestLiveBlog


class TestLiveBlogNewEntriesView(BaseIndexableTestCase):
    def setUp(self):
        super(TestLiveBlogNewEntriesView, self).setUp()

        self.liveblog = TestLiveBlog.objects.create(
            published=datetime.now())

        self.entry1 = LiveBlogEntry.objects.create(
            liveblog=self.liveblog,
            published=datetime.now())

    def test_requires_entry_ids_param(self):
        view = LiveblogNewEntriesView.as_view()
        with self.assertRaises(ValueError):
            view(
                RequestFactory().get('/liveblog/this-cool-liveblog-{}/new-entries'.format(
                    self.liveblog.pk)),
                slug='this-cool-live-blog',
                pk=self.liveblog.pk)

    def test_raises_404_if_liveblog_does_not_exist(self):
        view = LiveblogNewEntriesView.as_view()
        with self.assertRaises(Http404):
            view(
                RequestFactory().get('/liveblog/this-cool-liveblog-1234/new-entries'),
                slug='this-cool-live-blog',
                pk=1234)

    def test_renders_new_entries(self):
        entry2 = LiveBlogEntry.objects.create(
            liveblog=self.liveblog,
            published=datetime.now() - timedelta(days=1))
        entry3 = LiveBlogEntry.objects.create(
            liveblog=self.liveblog,
            published=datetime.now() - timedelta(days=1))

        view = LiveblogNewEntriesView.as_view()
        response = view(
            RequestFactory().get(
                '/liveblog/this-cool-liveblog-{}/new-entries?entry_ids={}'.format(
                    self.liveblog.pk, ','.join([str(entry2.pk), str(entry3.pk)]))),
                slug='this-cool-live-blog',
                pk=self.liveblog.pk)
        self.assertContains(response, '<bulbs-liveblog-entry', count=2)
        self.assertContains(response, 'entry-id="{}"'.format(entry2.pk))
        self.assertContains(response, 'entry-id="{}"'.format(entry3.pk))

    def test_only_renders_published_entries(self):
        entry2 = LiveBlogEntry.objects.create(
            liveblog=self.liveblog,
            published=datetime.now() - timedelta(days=1))
        entry3 = LiveBlogEntry.objects.create(
            liveblog=self.liveblog,
            published=datetime.now() + timedelta(days=1))
        LiveBlogEntry.objects.create(
            liveblog=self.liveblog)

        view = LiveblogNewEntriesView.as_view()
        response = view(
            RequestFactory().get(
                '/liveblog/this-cool-liveblog-{}/new-entries?entry_ids={}'.format(
                    self.liveblog.pk, ','.join([str(entry2.pk), str(entry3.pk)]))),
                slug='this-cool-live-blog',
                pk=self.liveblog.pk)
        self.assertContains(response, '<bulbs-liveblog-entry', count=1)
        self.assertContains(response, 'entry-id="{}"'.format(entry2.pk))
