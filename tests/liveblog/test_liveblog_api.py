from datetime import datetime, timedelta
import json

from model_mommy import mommy
import six
from six.moves.urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.liveblog.models import LiveBlogEntry, LiveBlogResponse
from bulbs.utils.test import BaseAPITestCase, make_content

from example.testcontent.models import TestLiveBlog


class TestLiveBlogEntryApi(BaseAPITestCase):

    def test_create_entry(self):
        content = make_content(_quantity=3)
        authors = mommy.make(get_user_model(), _quantity=2)
        liveblog = mommy.make(TestLiveBlog)
        data = {
            "liveblog": liveblog.id,
            "headline": "Something Really Funny",
            "authors": [a.id for a in authors],
            "body": "Why are you reading this? Stop it.",
            "recirc_content": [c.id for c in content],
            "published": "2015-01-02T03:04:05Z",
            "responses": [
                {
                    "author": authors[0].id,
                    "body": "First response"
                },
                {
                    "author": authors[1].id,
                    "body": "Second response"
                }
            ]
        }
        resp = self.api_client.post(reverse('liveblog-entry-list'),
                                    data=json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(resp.status_code, 201)

        self.assertDictContainsSubset(data, resp.data)

        entry = LiveBlogEntry.objects.get(id=resp.data['id'])
        self.assertEqual(entry.liveblog, liveblog)
        self.assertEqual(entry.headline, data['headline'])
        self.assertEqual(entry.body, data['body'])
        self.assertEqual(entry.published, datetime(2015, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
        six.assertCountEqual(self, entry.authors.all(), authors)
        six.assertCountEqual(self, entry.recirc_content.all(), content)

        responses = entry.responses.all()
        self.assertEqual(len(responses), 2)
        self.assertEqual(responses[0].body, 'First response')
        self.assertEqual(responses[0].author, authors[0])
        self.assertEqual(responses[0].ordering, 0)
        self.assertEqual(responses[1].body, 'Second response')
        self.assertEqual(responses[1].author, authors[1])
        self.assertEqual(responses[1].ordering, 1)

        # Verify backref
        self.assertEqual(1, liveblog.entries.count())
        self.assertEqual(entry, liveblog.entries.first())

    def test_get_list_empty(self):
        resp = self.api_client.get(reverse('liveblog-entry-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_get_list(self):
        liveblog = mommy.make(TestLiveBlog)
        entries = mommy.make(LiveBlogEntry, liveblog=liveblog, _quantity=3)
        resp = self.api_client.get(reverse('liveblog-entry-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 3)
        six.assertCountEqual(self,
                             [e['id'] for e in resp.data['results']],
                             [e.id for e in entries])

    def test_get_entry(self):
        entry = mommy.make(LiveBlogEntry)
        resp = self.api_client.get(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], entry.id)

    def test_update_entry(self):
        content = make_content()
        author = mommy.make(get_user_model())
        liveblog = mommy.make(TestLiveBlog)
        entry = mommy.make(LiveBlogEntry, liveblog=liveblog)
        orig_response = mommy.make(LiveBlogResponse, entry=entry, author=author, body='Original',
                                   ordering=0)
        data = {
            "liveblog": liveblog.id,
            "headline": "Updated Headline",
            "authors": [author.id],
            "body": "Updated Body",
            "recirc_content": [content.id],
            "published": "2015-02-02T02:02:02Z",
            "responses": [
                {
                    "author": author.id,
                    "body": "New Response 1"
                },
                {
                    "author": author.id,
                    "body": "New Response 2"
                }
            ]
        }
        self.give_permissions()
        resp = self.api_client.put(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}),
                                   data=json.dumps(data),
                                   content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], entry.id)
        self.assertEqual(resp.data['headline'], 'Updated Headline')
        entry.refresh_from_db()
        self.assertEqual(entry.liveblog, liveblog)
        self.assertEqual(entry.headline, 'Updated Headline')
        self.assertEqual(entry.body, data['body'])
        self.assertEqual(entry.published, datetime(2015, 2, 2, 2, 2, 2, tzinfo=timezone.utc))
        six.assertCountEqual(self, entry.authors.all(), [author])
        six.assertCountEqual(self, entry.recirc_content.all(), [content])

        responses = entry.responses.all()
        self.assertEqual(len(responses), 2)

        self.assertEqual(responses[0].body, 'New Response 1')
        self.assertEqual(responses[0].author, author)
        self.assertEqual(responses[0].ordering, 0)

        self.assertEqual(responses[1].body, 'New Response 2')
        self.assertEqual(responses[1].author, author)
        self.assertEqual(responses[1].ordering, 1)

        # Verify original response was deleted
        with self.assertRaises(LiveBlogResponse.DoesNotExist):
            orig_response.refresh_from_db()

        # Verify backref
        self.assertEqual(1, liveblog.entries.count())
        self.assertEqual(entry, liveblog.entries.first())

    def test_liveblog_filter(self):
        liveblogs = mommy.make(TestLiveBlog, _quantity=5)
        entries = [mommy.make(LiveBlogEntry, liveblog=liveblog, _quantity=2)
                   for liveblog in liveblogs]
        resp = self.api_client.get(reverse('liveblog-entry-list') +
                                   '?liveblog_id={}'.format(liveblogs[0].id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 2)
        six.assertCountEqual(self,
                             [e['id'] for e in resp.data['results']],
                             [e.id for e in entries[0]])


class TestPublicLiveBlogEntryApi(BaseAPITestCase):

    def test_read_only(self):
        for method in [self.api_client.post,
                       self.api_client.put]:
            self.assertEquals(405, method(reverse('public-liveblog-entry'),
                                          content_type="application/json").status_code)

    def test_list_if_modified_since(self):
        now = timezone.now()
        liveblog = mommy.make(TestLiveBlog)
        entries = [mommy.make(LiveBlogEntry, liveblog=liveblog, published=(now + timedelta(days=i)))
                   for i in range(5)]

        def check(days, expected_entries, expected_status_code=200):
            when = now + timedelta(days=days)
            resp = self.api_client.get(
                reverse('public-liveblog-entry') + '?{}'.format(
                    urlencode({'if_modified_since': when.isoformat()})))

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data['count'], len(expected_entries))
            self.assertEqual([e['id'] for e in resp.data['results']],
                             [e.id for e in expected_entries])

        check(days=-1, expected_entries=entries)
        check(days=0, expected_entries=entries[1:])
        check(days=3, expected_entries=entries[4:])
        check(days=4, expected_entries=[], expected_status_code=304)

    def test_list_invalid_if_modified_since(self):
        resp = self.api_client.get(reverse('public-liveblog-entry') + '?if_modified_since=ABC')
        self.assertEqual(resp.status_code, 400)
