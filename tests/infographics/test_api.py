import json
from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.infographics.enum import InfographicType
from bulbs.infographics.models import BaseInfographic
from bulbs.utils.test import BaseAPITestCase


class BaseInfographicTestCase(BaseAPITestCase):

    def test_post_list_no_data(self):
        data = self.list_data
        data.pop("data")
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)

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
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.timeline_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, self.timeline_data.get("data"))

    def test_post_strongside_weakside(self):
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.strongside_weakside_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, self.strongside_weakside_data.get("data"))

    def test_post_pro_con(self):
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.pro_con_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, self.pro_con_data.get("data"))

    def test_post_comparison(self):
        resp = self.api_client.post(
            self.list_endpoint,
            data=json.dumps(self.comparison_data),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        infographic = BaseInfographic.objects.get(id=resp.data["id"])
        self.assertEqual(infographic.data, self.comparison_data.get("data"))

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
                "items": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy",
                        OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ]),
                    ), (
                        "title", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Title"),
                            ("field_size", "short")
                        ]),
                    ), (
                        "image", OrderedDict([
                            ("type", "image"),
                            ("required", False),
                            ("read_only", False),
                            ("label", "Image")
                        ]),
                    )]))
                ]),
            }
        })

    def test_options_timeline(self):
        info = BaseInfographic.objects.create(
            title="Drake is good.",
            infographic_type=InfographicType.TIMELINE,
            data=self.list_data.get("data")
        )
        url = self.get_detail_endpoint(info.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)
        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            "fields": {
                "items": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ])), (
                        "title", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Title"),
                            ("field_size", "short")
                        ])), (
                        "image", OrderedDict([
                            ("type", "image"),
                            ("required", False),
                            ("read_only", False),
                            ("label", "Image")
                        ]))
                    ]))
                ])
            }
        })

    def test_options_strongside_weakside(self):
        info = BaseInfographic.objects.create(
            title="Drake is good.",
            infographic_type=InfographicType.STRONGSIDE_WEAKSIDE,
            data=self.strongside_weakside_data.get("data")
        )
        url = self.get_detail_endpoint(info.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)
        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            "fields": {
                "body": OrderedDict([
                    ("type", "richtext"),
                    ("required", True),
                    ("read_only", False),
                    ("field_size", "long")
                ]),
                "strong": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ]))
                    ]))
                ]),
                "weak": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ]))
                    ]))
                ]),
            }
        })

    def test_options_pro_con(self):
        info = BaseInfographic.objects.create(
            title="Drake is good.",
            infographic_type=InfographicType.PRO_CON,
            data=self.pro_con_data.get("data")
        )
        url = self.get_detail_endpoint(info.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)
        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            "fields": {
                "body": OrderedDict([
                    ("type", "richtext"),
                    ("required", True),
                    ("read_only", False),
                    ("field_size", "long")
                ]),
                "con": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([
                        ("copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ]))
                    ]))
                ]),
                "pro": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([
                        ("copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Copy"),
                            ("field_size", "long")
                        ]))
                    ]))
                ])
            }
        })

    def test_options_comparison(self):
        info = BaseInfographic.objects.create(
            title="Drake is good.",
            infographic_type=InfographicType.COMPARISON,
            data=self.comparison_data.get("data")
        )
        url = self.get_detail_endpoint(info.pk)
        resp = self.api_client.options(url)
        self.assertEqual(resp.status_code, 200)
        fields = resp.data.get("fields")
        data_field = fields.get("data")
        self.assertEqual(data_field, {
            "fields": {
                "items": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([
                        (
                            "title", OrderedDict([
                                ("type", "richtext"),
                                ("required", True),
                                ("read_only", False),
                                ("label", "Title"),
                                ("field_size", "short")
                            ])
                        ), (
                            "copy_x", OrderedDict([
                                ("type", "richtext"),
                                ("required", True),
                                ("read_only", False),
                                ("label", "Copy x"),
                                ("field_size", "long")
                            ])
                        ), (
                            "copy_y", OrderedDict([
                                ("type", "richtext"),
                                ("required", True),
                                ("read_only", False),
                                ("label", "Copy y"),
                                ("field_size", "long")
                            ])
                        )
                    ]))
                ]),
                "key_x": OrderedDict([
                    (
                        "title", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Title"),
                            ("field_size", "short")
                        ])
                    ), (
                        "color", OrderedDict([
                            ("type", "string"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Color")
                        ]),
                    ), (
                        "initial", OrderedDict([
                            ("type", "string"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Initial")
                        ])
                    )
                ]),
                "key_y": OrderedDict([
                    (
                        "title", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Title"),
                            ("field_size", "short")
                        ])
                    ), (
                        "color", OrderedDict([
                            ("type", "string"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Color")
                        ]),
                    ), (
                        "initial", OrderedDict([
                            ("type", "string"),
                            ("required", True),
                            ("read_only", False),
                            ("label", "Initial")
                        ])
                    )
                ]),
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
    def timeline_data(self):
        return {
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

    @property
    def strongside_weakside_data(self):
        return {
            "title": "KILL ME",
            "infographic_type": InfographicType.STRONGSIDE_WEAKSIDE,
            "data": {
                "body": "It's body time!",
                "strong": [{"copy": "glo strong"}],
                "weak": [{"copy": "glo weak"}]
            }
        }

    @property
    def pro_con_data(self):
        return {
            "title": "KILL ME",
            "infographic_type": InfographicType.PRO_CON,
            "data": {
                "body": "Pro Con Body",
                "pro": [{"copy": "did it"}],
                "con": [{"copy": "not so much my dudes."}]
            }
        }

    @property
    def comparison_data(self):
        return {
            "title": "KILL ME",
            "infographic_type": InfographicType.COMPARISON,
            "data": {
                "key_x": {
                    "title": "Yassss queen",
                    "color": "BLUE!",
                    "initial": "A!"
                },
                "key_y": {
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

    @property
    def list_endpoint(self):
        return reverse("content-list") + "?doctype=" + self.doc_type

    @property
    def doc_type(self):
        return BaseInfographic.search_objects.mapping.doc_type
