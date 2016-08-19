from datetime import timedelta
import json

from model_mommy import mommy
import six
from six.moves.urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.liveblog.models import LiveBlogEntry
from bulbs.utils.test import BaseAPITestCase

from example.testcontent.models import TestLiveBlog


class TestLiveBlogApi(BaseAPITestCase):

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_get(self):
        pass

    def test_list(self):
        pass


class TestLiveBlogEntryApi(BaseAPITestCase):

    def test_create(self):
        liveblog = mommy.make(TestLiveBlog)
        data = {
            "liveblog": liveblog.id,
            "headline": "Something Really Funny",
            "authors": [
                # TODO
            ],
            "body": "Why are you reading this? Stop it.",
            "recirc_content": [
                # TODO
            ],
            "published": "2015-01-01T01:01:00Z",
            # TODO
            # "responses": [
            #     {
            #         "author": "TODO",
            #         "body": "Some more really interesting stuff you should read."
            #     }
            # ]
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
        # TODO: Check more fields

    def test_list_empty(self):
        resp = self.api_client.get(reverse('liveblog-entry-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_list(self):
        liveblog = mommy.make(TestLiveBlog)
        entries = mommy.make(LiveBlogEntry, liveblog=liveblog, _quantity=3)
        resp = self.api_client.get(reverse('liveblog-entry-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 3)
        six.assertCountEqual(self,
                             [e['id'] for e in resp.data['results']],
                             [e.id for e in entries])

    def test_list_if_modified_since(self):
        now = timezone.now()
        liveblog = mommy.make(TestLiveBlog)
        entries = [mommy.make(LiveBlogEntry, liveblog=liveblog, published=(now + timedelta(days=i)))
                   for i in range(5)]

        def check(days, expected_entries, expected_status_code=200):
            when = now + timedelta(days=days)
            resp = self.api_client.get(
                reverse('liveblog-entry-list') + '?{}'.format(
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
        resp = self.api_client.get(reverse('liveblog-entry-list') + '?if_modified_since=ABC')
        self.assertEqual(resp.status_code, 400)

    def test_detail_get(self):
        entry = mommy.make(LiveBlogEntry)
        resp = self.api_client.get(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], entry.id)

    def test_detail_update(self):
        liveblog = mommy.make(TestLiveBlog)
        entry = mommy.make(LiveBlogEntry, liveblog=liveblog)
        data = {
            "liveblog": liveblog.id,
            "headline": "Updated Headline",
            "authors": [
                # TODO
            ],
            "body": "Updated Body",
            "recirc_content": [
                # TODO
            ],
            "published": "2015-02-02T02:02:00Z",
            # TODO
            # "responses": [
            #     {
            #         "author": "TODO",
            #         "body": "Some more really interesting stuff you should read."
            #     }
            # ]
        }
        self.give_permissions()
        resp = self.api_client.put(reverse('liveblog-entry-detail', kwargs={'pk': entry.id}),
                                   data=json.dumps(data),
                                   content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], entry.id)
        self.assertEqual(resp.data['headline'], 'Updated Headline')
        entry.refresh_from_db()
        self.assertEqual(entry.headline, 'Updated Headline')
