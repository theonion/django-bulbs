import json
from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.infographics.enum import InfographicType
from bulbs.infographics.models import BaseInfographic
from bulbs.utils.test import BaseAPITestCase


class BaseInfographicTestCase(BaseAPITestCase):

    def test_post_list(self):
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.list_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, self.list_data.get("data"))

    def test_post_timeline(self):
        info_data = {
            "title": "KILL ME",
            "infographic_type": InfographicType.TIMELINE,
            "data": {
                "items": [{
                    "title": "Michael Bayless",
                    "copy": "How did he do that?",
                    "image": {"id": 1}
                }]
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(info_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, info_data.get("data"))

    def test_post_strongside_weakside(self):
        info_data = {
            "title": "KILL ME",
            "infographic_type": InfographicType.STRONGSIDE_WEAKSIDE,
            "data": {
                "body": "It's body time!",
                "strong": [{"copy": "glo strong"}],
                "weak": [{"copy": "glo weak"}]
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(info_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, info_data.get("data"))

    def test_post_pro_con(self):
        info_data = {
            "title": "KILL ME",
            "infographic_type": InfographicType.PRO_CON,
            "data": {
                "body": "Pro Con Body",
                "pro": [{"copy": "did it"}],
                "con": [{"copy": "not so much my dudes."}]
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(info_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, info_data.get("data"))

    def test_post_comparison(self):
        info_data = {
            "title": "KILL ME",
            "infographic_type": InfographicType.COMPARISON,
            "data": {
                "key": {
                    "title": "Yassss queen",
                    "color": "BLUE!",
                    "initial": "A!"
                },
                "items": [{
                    "title": "Michael Bayless",
                    "copy_x": "How did he do that?",
                    "copy_y": "How didn't he do that?"
                }]
            }
        }
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(info_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, info_data.get("data"))

    def test_options_list(self):
        info = BaseInfographic.objects.create(
            title="Drake is good.",
            infographic_type=InfographicType.LIST,
            data=self.list_data.get("data")
        )
        url = self.get_detail_endpoint(info.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)
        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            "fields": {
                "is_numbered": OrderedDict([
                    ("type", "boolean"),
                    ("required", False),
                    ("read_only", False)
                ]),
                "items": OrderedDict([(
                    "copy",
                    OrderedDict([
                        ("type", "string"),
                        ("required", True),
                        ("read_only", False),
                        ("label", "Copy")
                    ]),
                ), (
                    "title", OrderedDict([
                        ("type", "string"),
                        ("required", True),
                        ("read_only", False),
                        ("label", "Title")
                    ]),
                ), (
                    "image", OrderedDict([
                        ("type", "field"),
                        ("required", False),
                        ("read_only", False),
                        ("label", "Image")
                    ]),
                )]),
            }
        })

    def get_detail_endpoint(self, pk):
        return reverse("content-detail", kwargs={"pk": pk})

    @property
    def list_data(self):
        return {
            "title": "Hiya!",
            "infographic_type": InfographicType.LIST,
            "data": {
                "is_numbered": True,
                "items": [{
                    "title": "Michael Bayless",
                    "copy": "How did he do that?",
                    "image": {"id": 1}
                }]
            }
        }

    @property
    def list_endpoint(self):
        return reverse("content-list") + "?doctype=" + self.doc_type

    @property
    def doc_type(self):
        return BaseInfographic.search_objects.mapping.doc_type
