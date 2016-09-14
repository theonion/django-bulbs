from datetime import datetime
import json

from model_mommy import mommy
import six

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.liveblog.models import LiveBlogEntry, LiveBlogResponse
from bulbs.utils.test import BaseAPITestCase, make_content

from example.testcontent.models import TestLiveBlog


class TestLiveBlogApi(BaseAPITestCase):

    def test_create_minimal_liveblog(self):

        author = get_user_model().objects.create(username="mparent")
        data = {
            "title": "Mike Test",
            "authors": [{"username": "mparent"}]
        }
        resp = self.api_client.post(
            reverse("content-list") + "?doctype=testcontent_testliveblog",
            data=json.dumps(data),
            content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        liveblog = TestLiveBlog.objects.get(id=resp.data['id'])
        self.assertEqual('Mike Test', liveblog.title)
        self.assertEqual(1, liveblog.authors.count())
        self.assertEqual(author, liveblog.authors.first())


class TestLiveBlogEntryApi(BaseAPITestCase):

    def test_create_entry(self):
        content = make_content(_quantity=3)
        authors = mommy.make(get_user_model(), _quantity=5)
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
                    "author": authors[i].id,
                    "body": "New Response {}".format(i),
                    "internal_name": "Internal {}".format(i)
                }
                for i in range(5)

            ]
        }
        resp = self.api_client.post(reverse('liveblog-entry-list'),
                                    data=json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(resp.status_code, 201)

        UNORDERED_KEYS = ['authors', 'recirc_content']
        self.assertDictContainsSubset({k: v for k, v in data.items()
                                       if k not in UNORDERED_KEYS},
                                      resp.data)
        for key in UNORDERED_KEYS:
            six.assertCountEqual(self, data[key], resp.data[key])

        entry = LiveBlogEntry.objects.get(id=resp.data['id'])
        self.assertEqual(entry.liveblog, liveblog)
        self.assertEqual(entry.headline, data['headline'])
        self.assertEqual(entry.body, data['body'])
        self.assertEqual(entry.published, datetime(2015, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
        six.assertCountEqual(self, entry.authors.all(), authors)
        six.assertCountEqual(self, entry.recirc_content.all(), content)

        responses = entry.responses.all()
        self.assertEqual(len(responses), 5)
        for i, response in enumerate(responses):
            self.assertEqual(response.author, authors[i])
            self.assertEqual(response.ordering, i)
            self.assertEqual(response.body, 'New Response {}'.format(i))
            self.assertEqual(response.internal_name, 'Internal {}'.format(i))

        # Verify backref
        self.assertEqual(1, liveblog.entries.count())
        self.assertEqual(entry, liveblog.entries.first())

    def test_create_minimal_entry(self):
        liveblog = mommy.make(TestLiveBlog)
        data = {
            "liveblog": liveblog.id,
        }
        resp = self.api_client.post(reverse('liveblog-entry-list'),
                                    data=json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(resp.status_code, 201)

    def test_create_minimal_entry_response(self):
        liveblog = mommy.make(TestLiveBlog)
        data = {
            "liveblog": liveblog.id,
            "responses": [
                {
                    "body": "New Response",
                }
            ]
        }
        resp = self.api_client.post(reverse('liveblog-entry-list'),
                                    data=json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(resp.status_code, 201)

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
                    "body": "New Response {}".format(i),
                    "internal_name": "Internal {}".format(i)
                }
                for i in range(10)
            ]
        }
        self.give_permissions()
        resp = self.api_client.put(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}),
                                   data=json.dumps(data),
                                   content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        self.assertDictContainsSubset(data, resp.data)
        self.assertEqual(resp.data['id'], entry.id)

        entry.refresh_from_db()
        self.assertEqual(entry.liveblog, liveblog)
        self.assertEqual(entry.headline, 'Updated Headline')
        self.assertEqual(entry.body, 'Updated Body')
        self.assertEqual(entry.published, datetime(2015, 2, 2, 2, 2, 2, tzinfo=timezone.utc))
        six.assertCountEqual(self, entry.authors.all(), [author])
        six.assertCountEqual(self, entry.recirc_content.all(), [content])

        responses = entry.responses.all()
        self.assertEqual(len(responses), 10)
        for i, response in enumerate(responses):
            self.assertEqual(response.author, author)
            self.assertEqual(response.ordering, i)
            self.assertEqual(response.body, 'New Response {}'.format(i))
            self.assertEqual(response.internal_name, 'Internal {}'.format(i))

        # Verify original response was deleted
        with self.assertRaises(LiveBlogResponse.DoesNotExist):
            orig_response.refresh_from_db()
        self.assertEqual(10, LiveBlogResponse.objects.count())

        # Verify backref
        self.assertEqual(1, liveblog.entries.count())
        self.assertEqual(entry, liveblog.entries.first())

    def test_delete_entry(self):
        liveblog = mommy.make(TestLiveBlog)
        entry = mommy.make(LiveBlogEntry, liveblog=liveblog)

        self.assertEqual(1, liveblog.entries.count())

        resp = self.api_client.delete(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}))
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(0, liveblog.entries.count())

        with self.assertRaises(LiveBlogEntry.DoesNotExist):
            entry.refresh_from_db()
        self.assertEqual(0, LiveBlogEntry.objects.count())

    def test_liveblog_filter(self):
        liveblogs = mommy.make(TestLiveBlog, _quantity=5)
        entries = [mommy.make(LiveBlogEntry, liveblog=liveblog, _quantity=2)
                   for liveblog in liveblogs]
        resp = self.api_client.get(reverse('liveblog-entry-list') +
                                   '?liveblog={}'.format(liveblogs[0].id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 2)
        six.assertCountEqual(self,
                             [e['id'] for e in resp.data['results']],
                             [e.id for e in entries[0]])
