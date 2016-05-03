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


class GlanceFeedTestCase(BaseIndexableTestCase):

    maxDiff = None  # TEMP DEBUG

    def test_empty(self):
        resp = Client().get(reverse('glance-feed'))
        self.assertEqual(200, resp.status_code)
        self.assertEqual('application/json', resp['content-type'])
        self.assertEqual(json.loads(resp.content.decode('utf-8')), {'items': []})

    @override_settings(BETTY_IMAGE_URL='http://images.onionstatic.com/onion')
    @freeze_time('2016-5-3 10:11:12')
    def test_single_item(self):

        content = make_content(
            TestContentObj,
            id=52852,
            title='The Pros And Cons Of Taking A Gap Year',
            published=datetime(2016, 5, 2, 14, 43, 0, tzinfo=timezone.utc),
            thumbnail_override=53338,
            _quantity=1)[0]
        for name in ['College', 'Technology']:
            content.tags.add(Tag.objects.create(name=name))
        content.save()

        TestContentObj.search_objects.refresh()

        resp = Client().get(reverse('glance-feed'), SERVER_NAME='www.theonion.com')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('application/json', resp['content-type'])
        self.assertEqual(
            json.loads(resp.content.decode('utf-8')),
            {
                'items': [{
                    'type': 'post',
                    'id': 52852,
                    'title': 'The Pros And Cons Of Taking A Gap Year',
                    'link': 'http://www.theonion.com/detail/52852/',
                    'modified': '2016-05-03T10:11:12+00:00',
                    'published': '2016-05-02T14:43:00+00:00',
                    'slug': 'the-pros-and-cons-of-taking-a-gap-year',
                    'featured_media': {
                        'type': 'image',
                        'image': 'http://images.onionstatic.com/onion/5333/8/1x1/600.jpg',
                        'markup': ''
                    },
                    'authors': ["America's Finest News Source"],
                    'tags': {
                        'section': ['College', 'Technology']
                    }
                }]
            })

    def test_pagination(self):
        pass
