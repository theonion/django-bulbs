from datetime import datetime
import json

from freezegun import freeze_time

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import timezone

from bulbs.content.models import Tag
from bulbs.section.models import Section
from bulbs.utils.test import BaseIndexableTestCase, make_content

from example.testcontent.models import TestContentObj


@override_settings(BETTY_IMAGE_URL='//images.onionstatic.com/onion')
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
        section = Section.objects.create(name='Test Section')
        content = make_content(TestContentObj,
                               id=52852,
                               title='The Pros And Cons Of Taking A Gap Year',
                               body='<div>Test Body</div>',
                               published=datetime(2016, 5, 2, 14, 43, 0, tzinfo=timezone.utc),
                               description='Test Description',
                               thumbnail_override=53338,
                               tunic_campaign_id=300,
                               )
        tag = Tag.objects.create(name='College')
        content.tags.add(tag)

        resp = self.get_feed()
        self.assertEqual(
            resp,
            {
                'content': [{
                    'id': 52852,
                    'url': 'http://www.theonion.com/detail/52852/',
                    'title': 'The Pros And Cons Of Taking A Gap Year',
                    'authors': [
                        {'label': "America's Finest News Source",
                         'id': 0,  # TODO: correct?
                         },
                    ],
                    'published': '2016-05-02T14:43:00+00:00',
                    'modified': '2016-05-03T10:11:12+00:00',
                    'sections': [
                        {'id': section.id,
                         'label': 'Test Section',
                         },
                    ],
                    'description': 'Test Description',
                    'body': '<div>Test Body</div>',
                    'tags': [
                        {'id': tag.id,
                         'label': 'College'
                         },
                    ],
                    'type': 'article',
                    'feature_type': '',  # TODO
                    'images': {
                        '//images.onionstatic.com/onion/5333/8/16x9/600.jpg',
                    },
                    'videos': [
                         # TODO: Format?
                    ],
                    'campaign_id': 300,
                }],
                'page': 1,
                'per_page': 10,
                'total_items': 1,
                'next': None,
                # 'previous': None,
            })

    def test_multiple_pages(self):
        # TODO
        pass

    def test_default_author(self):
        # TODO
        pass

    def test_with_authors(self):
        # TODO
        pass

    def test_type_video(self):
        # TODO
        pass

    def test_type_graphic(self):
        # TODO
        pass

    def test_pagination_query_param(self):
        # TODO: Test '?per_page=<int>' query param
        pass

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
