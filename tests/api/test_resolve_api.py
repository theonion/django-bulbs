from datetime import timedelta
import six

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.content.models import Tag, Content
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseAPITestCase, make_content


class TestResolveSpecialCoverageAPI(BaseAPITestCase):

    def setUp(self):
        super(TestResolveSpecialCoverageAPI, self).setUp()
        biden_condition = {
            "values": [{
                "value": "joe-biden",
                "label": "Joe Biden"
            }],
            "type": "all",
            "field": "tag"
        }
        obama_condition = {
            "values": [{
                "value": "obama",
                "label": "Obama"
            }],
            "type": "all",
            "field": "tag"
        }
        biden_query = {
            "label": "Uncle Joe",
            "query": {
                "groups": [{
                    "conditions": [biden_condition]
                }]
            },
        }
        obama_query = {
            "label": "Obama",
            "query": {
                "groups": [{
                    "conditions": [obama_condition]
                }]
            },
        }

        for sc in [SpecialCoverage.objects.create(id=90,
                                                  name="Uncle Joe",
                                                  description="Classic Joeseph Biden",
                                                  query=biden_query),
                   SpecialCoverage.objects.create(id=91,
                                                  name="Obama",
                                                  description="Classic Obama",
                                                  query=obama_query),
                   ]:
            # Manually index this percolator
            sc._save_percolator()

    def resolve(self, **data):
        return self.api_client.get(reverse("special-coverage-resolve-list"),
                                   data=data, format="json")

    def test_found_one(self):
        # Add some content
        content = Content.objects.create(
            id=123,
            title='a',
            published=timezone.now() - timedelta(hours=1),
        )
        content.tags.add(Tag.objects.create(name='joe-biden'))
        content.save()
        Content.search_objects.refresh()

        r = self.resolve(content_id=123)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(1, len(r.data))
        data = r.data[0]
        self.assertEqual(90, data['id'])
        self.assertEqual('Uncle Joe', data['name'])

    def test_found_multiple(self):
        # Add some content
        content = Content.objects.create(
            id=123,
            title='a',
            published=timezone.now() - timedelta(hours=1),
        )
        content.tags.add(Tag.objects.create(name='joe-biden'))
        content.tags.add(Tag.objects.create(name='obama'))
        content.save()
        Content.search_objects.refresh()

        r = self.resolve(content_id=123)
        self.assertEqual(r.status_code, 200)
        six.assertCountEqual(self, [90, 91], [r['id'] for r in r.data])

    def test_no_special_coverage(self):
        make_content(id=123)
        r = self.resolve(content_id=123)
        self.assertEqual(r.status_code, 204)

    def test_invalid_content(self):
        r = self.resolve(content_id=123)
        self.assertEqual(r.status_code, 404)
