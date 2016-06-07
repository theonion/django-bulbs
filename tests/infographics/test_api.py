import json

from django.core.urlresolvers import reverse

from bulbs.infographics.enum import InfographicType
from bulbs.infographics.models import BaseInfographic
from bulbs.utils.test import BaseAPITestCase


class BaseInfographicTestCase(BaseAPITestCase):

    def test_post_list(self):
        info_data = {
            "title": "KILL ME",
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
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(info_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, info_data.get("data"))

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

    @property
    def list_endpoint(self):
        doc_type = BaseInfographic.search_objects.mapping.doc_type
        return reverse("content-list") + "?doctype=" + doc_type
