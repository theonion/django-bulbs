from datetime import timedelta
import six

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.content.models import Tag, Content
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.utils.test import BaseAPITestCase


class TestResolveSpecialCoverageAPI(BaseAPITestCase):

    def make_special_coverage(self, pk, name, **kw):
        condition = {
            "values": [{
                "value": name,
                "label": name
            }],
            "type": "all",
            "field": "tag"
        }
        query = {
            "label": name,
            "query": {
                "groups": [{
                    "conditions": [condition]
                }]
            },
        }
        sc = SpecialCoverage.objects.create(pk=pk,
                                            name=name,
                                            # description="",
                                            query=query,
                                            **kw)
        sc._save_percolator()
        return sc

    def make_content(self, id, tags=None):
        content = Content.objects.create(
            id=id,
            title='a',
            published=timezone.now() - timedelta(hours=1),
        )
        for name in (tags or []):
            content.tags.add(Tag.objects.get_or_create(name=name)[0])
        content.save()
        Content.search_objects.refresh()
        return content

    def resolve(self, expected_status_code=200, **data):
        resp = self.api_client.get(reverse("special-coverage-resolve-list"),
                                   data=data, format="json")
        self.assertEqual(expected_status_code, resp.status_code)
        return resp

    def test_found_one(self):
        self.make_special_coverage(90, 'joe-biden')
        self.make_content(id=123, tags=['joe-biden'])

        resp = self.resolve(content_id=123)
        self.assertEqual(1, len(resp.data))
        data = resp.data[0]
        self.assertEqual(90, data['id'])
        self.assertEqual('joe-biden', data['name'])

    def test_found_multiple(self):
        self.make_special_coverage(90, 'obama')
        self.make_special_coverage(91, 'joe-biden')
        self.make_content(id=123, tags=['joe-biden', 'obama'])

        resp = self.resolve(content_id=123)
        six.assertCountEqual(self, [90, 91], [r['id'] for r in resp.data])

    def test_no_special_coverage_tag(self):
        self.make_special_coverage(90, 'obama')
        self.make_content(id=123)

        self.resolve(content_id=123, expected_status_code=204)

    def test_invalid_content(self):
        self.resolve(content_id=123, expected_status_code=404)

    def test_filter_sponsored(self):
        self.make_special_coverage(90, 'obama', tunic_campaign_id=2001)
        self.make_special_coverage(91, 'joe-biden')
        self.make_content(id=123, tags=['joe-biden', 'obama'])

        resp = self.resolve(content_id=123, sponsored=True)
        six.assertCountEqual(self, [90], [r['id'] for r in resp.data])

    def test_filter_not_sponsored(self):
        self.make_special_coverage(90, 'obama', tunic_campaign_id=2001)
        self.make_special_coverage(91, 'joe-biden')
        self.make_content(id=123, tags=['joe-biden', 'obama'])

        resp = self.resolve(content_id=123, sponsored=False)
        six.assertCountEqual(self, [91], [r['id'] for r in resp.data])

    def test_filter_active(self):
        self.make_special_coverage(90, 'joe-biden',
                                   start_date=(timezone.now() + timedelta(days=1)),
                                   end_date=(timezone.now() + timedelta(days=2)),
                                   )
        self.make_special_coverage(91, 'obama',
                                   start_date=(timezone.now() - timedelta(days=1)),
                                   end_date=(timezone.now() + timedelta(days=1)),
                                   )
        self.make_content(id=123, tags=['joe-biden', 'obama'])

        resp = self.resolve(content_id=123, active=True)
        six.assertCountEqual(self, [91], [r['id'] for r in resp.data])

    def test_filter_not_active(self):
        self.make_special_coverage(90, 'joe-biden',
                                   start_date=(timezone.now() + timedelta(days=1)),
                                   end_date=(timezone.now() + timedelta(days=2)),
                                   )
        self.make_special_coverage(91, 'obama',
                                   start_date=(timezone.now() - timedelta(days=1)),
                                   end_date=(timezone.now() + timedelta(days=1)),
                                   )
        self.make_content(id=123, tags=['joe-biden', 'obama'])
        resp = self.resolve(content_id=123, active=False)
        six.assertCountEqual(self, [90], [r['id'] for r in resp.data])
