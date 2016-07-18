import json
from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseAPITestCase


class BaseSuperFeatureTestCase(BaseAPITestCase):

    def setUp(self):
        super(BaseSuperFeatureTestCase, self).setUp()
        self.doc_type = BaseSuperFeature.search_objects.mapping.doc_type
        self.list_endpoint = reverse("content-list") + "?doctype=" + self.doc_type

    def get_detail_endpoint(self, pk):
        return reverse("content-detail", kwargs={"pk": pk})

    def test_list_view_options(self):
        resp = self.api_client.options(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)

    def test_post_no_data(self):
        data = {
            "title": "Guide to Summer",
            "superfeature_type": GUIDE_TO_HOMEPAGE
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_guide_to(self):
        data = {
            "title": "Guide to Summer",
            "superfeature_type": GUIDE_TO_HOMEPAGE,
            "data": {
                "sponsor_text": "Presented by Reds",
                "sponsor_image": {"id": 1}
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

        superfeature = BaseSuperFeature.objects.get(id=resp.data["id"])
        self.assertEqual(superfeature.data, data.get("data"))

    def test_post_child_feature(self):
        data = {
            "title": "Guide to Summer",
            "superfeature_type": GUIDE_TO_HOMEPAGE,
            "data": {
                "sponsor_text": "Presented by Reds",
                "sponsor_image": {"id": 1}
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        parent_id = resp.data["id"]

        data = {
            "title": "Guide to Summer",
            "superfeature_type": GUIDE_TO_ENTRY,
            "parent": parent_id,
            "ordering": 1
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        child_id = resp.data["id"]

        # check that only the parent was indexed
        BaseSuperFeature.search_objects.refresh()
        results = self.es.search(
            BaseSuperFeature.search_objects.mapping.index,
            BaseSuperFeature.search_objects.mapping.doc_type
        )
        self.assertEqual(results['hits']['total'], 1)

        child = BaseSuperFeature.objects.get(id=child_id)
        parent = BaseSuperFeature.objects.get(id=parent_id)

        # CHECK IF PARENT AND ARE SETTING
        self.assertTrue(child.is_child)
        self.assertFalse(child.is_parent)
        self.assertEqual(child.ordering, 1)
        self.assertFalse(parent.is_child)
        self.assertTrue(parent.is_parent)

    def test_options_guide_to(self):
        base = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )

        url = self.get_detail_endpoint(base.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)

        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            'fields': {
                'sponsor_text': OrderedDict([
                    ('type', 'string'),
                    ('required', False),
                    ('read_only', False)
                ]),
                'sponsor_image': OrderedDict([
                    ('type', 'image'),
                    ('required', False),
                    ('read_only', False)
                ])
            }
        })

    def test_parent_get_children(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        child = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        url = reverse('content-relations', kwargs={'pk': parent.pk})
        resp = self.api_client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [
            OrderedDict([
                ('id', child.id),
                ('internal_name', None),
                ('title', 'Guide to Cats')
            ])
        ])
