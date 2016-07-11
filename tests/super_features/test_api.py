import json
from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.super_features.models import BaseSuperFeature, GUIDE_TO_HOME, GUIDE_TO_PAGE
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
            "superfeature_type": GUIDE_TO_HOME
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
            "superfeature_type": GUIDE_TO_HOME,
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

    def test_options_guide_to(self):
        pass
