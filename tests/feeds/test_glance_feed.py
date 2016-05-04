from datetime import datetime
import json

from freezegun import freeze_time

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import timezone

from bulbs.content.models import Tag
from bulbs.utils.test import BaseIndexableTestCase, make_content

from example.testcontent.models import TestContentObj


@override_settings(BETTY_IMAGE_URL='http://images.onionstatic.com/onion')
class GlanceFeedTestCase(BaseIndexableTestCase):

    maxDiff = None  # Show full diffs on error

    def get_feed(self, status_code=200, *args, **kwargs):
        TestContentObj.search_objects.refresh()
        resp = Client().get(reverse('glance-feed'), kwargs, SERVER_NAME='www.theonion.com')
        self.assertEqual(status_code, resp.status_code)
        if resp.status_code == 200:
            self.assertEqual('application/json', resp['content-type'])
            return json.loads(resp.content.decode('utf-8'))

    def test_empty(self):
        resp = self.get_feed()
        self.assertEqual(resp, {'count': 0,
                                'next': None,
                                'previous': None,
                                'results': []})

    @freeze_time('2016-5-3 10:11:12')
    def test_single_item(self):
        content = make_content(TestContentObj,
                               id=52852,
                               title='The Pros And Cons Of Taking A Gap Year',
                               published=datetime(2016, 5, 2, 14, 43, 0, tzinfo=timezone.utc),
                               thumbnail_override=53338)
        for name in ['College', 'Technology']:
            content.tags.add(Tag.objects.create(name=name))
        content.save()

        resp = self.get_feed()
        self.assertEqual(
            resp,
            {
                'count': 1,
                'next': None,
                'previous': None,
                'results': [{
                    'type': 'post',
                    'id': 52852,
                    'title': 'The Pros And Cons Of Taking A Gap Year',
                    'link': 'http://www.theonion.com/detail/52852/',
                    'modified': '2016-05-03T10:11:12+00:00',
                    'published': '2016-05-02T14:43:00+00:00',
                    'slug': 'the-pros-and-cons-of-taking-a-gap-year',
                    'featured_media': {
                        'type': 'image',
                        'image': 'http://images.onionstatic.com/onion/5333/8/16x9/600.jpg',
                        'markup': ''
                    },
                    'authors': ["America's Finest News Source"],
                    'tags': {
                        'section': ['College', 'Technology']
                    }
                }]
            })

    def test_pagination(self):
        make_content(TestContentObj,
                     published=datetime(2016, 5, 2, 14, 43, 0, tzinfo=timezone.utc),
                     _quantity=11)

        resp = self.get_feed(page=1, page_size=5)
        self.assertEqual(11, resp['count'])
        self.assertEqual(5, len(resp['results']))

        resp = self.get_feed(page=2, page_size=5)
        self.assertEqual(5, len(resp['results']))

        resp = self.get_feed(page=3, page_size=5)
        self.assertEqual(1, len(resp['results']))

    def test_pagination_bounds_404(self):
        # One page past last should trigger 404
        make_content(TestContentObj,
                     published=datetime(2016, 5, 2, 14, 43, 0, tzinfo=timezone.utc))
        self.get_feed(page=2, page_size=1, status_code=404)

    def test_sort_last_modified(self):
        now = timezone.now()
        content = make_content(TestContentObj,
                               published=now - timezone.timedelta(hours=1),
                               _quantity=5)
        # Stagger "last_modified" (an "auto_now" field)
        for c, offset in zip(content, [0, 4, 1, 3, 2]):
            with freeze_time(now - timezone.timedelta(hours=offset)):
                c.save()

        resp = self.get_feed()
        self.assertEqual([content[i].id for i in [0, 2, 4, 3, 1]],
                         [c['id'] for c in resp['results']])

    def test_filter_published(self):
        content = make_content(TestContentObj, published=None)
        self.assertEqual(0, self.get_feed()['count'])
        content.published = timezone.now() - timezone.timedelta(hours=1)
        content.save()
        self.assertEqual(1, self.get_feed()['count'])
