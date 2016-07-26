import json
from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.infographics.enum import InfographicType
from bulbs.infographics.models import BaseInfographic
from bulbs.utils.test import BaseAPITestCase


class BaseInfographicTestCase(BaseAPITestCase):

    def test_list_view_options(self):
        resp = self.api_client.options(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)

    def test_list_view_get(self):
        """
        checks for `initial_data` bug.

        If infographic data exists, a 500 is raised for content-list `GET`.
        """
        BaseInfographic.objects.create(
            title='Money cammy baby',
            infographic_type=InfographicType.LIST,
            data=self.list_data
        )
        endpoint = reverse('content-list') + "?page=1"
        resp = self.api_client.get(endpoint)
        self.assertEqual(resp.status_code, 200)

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
        expected_data = self.list_data.get('data')
        expected_data['entries'][1] = {
            'title': expected_data['entries'][1]['title'],
            'image': None,
            'copy': expected_data['entries'][1]['copy']
        }
        expected_data['entries'][2]['image'] = None
        self.assertEqual(infographic.data, expected_data)

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
                "entries": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy",
                        OrderedDict([
                            ("field_size", "long"),
                            ("label", "Copy"),
                            ("read_only", False),
                            ("required", True),
                            ("type", "richtext")
                        ]),
                    ), (
                        "title", OrderedDict([
                            ("field_size", "short"),
                            ("label", "Title"),
                            ("read_only", False),
                            ("required", False),
                            ("type", "richtext")
                        ]),
                    ), (
                        "image", OrderedDict([
                            ("label", "Image"),
                            ("read_only", False),
                            ("required", False),
                            ("type", "image")
                        ]),
                    )])),
                    ("child_label", "entry")
                ]),
                "is_numbered": OrderedDict([
                    ("read_only", False),
                    ("required", False),
                    ("type", "boolean")
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
                "entries": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("field_size", "long"),
                            ("label", "Copy"),
                            ("required", True),
                            ("read_only", False),
                            ("type", "richtext")
                        ])), (
                        "title", OrderedDict([
                            ("field_size", "short"),
                            ("label", "Title"),
                            ("read_only", False),
                            ("required", False),
                            ("type", "richtext"),
                        ])), (
                        "image", OrderedDict([
                            ("label", "Image"),
                            ("read_only", False),
                            ("required", False),
                            ("type", "image")
                        ]))
                    ])),
                    ("child_label", "entry")
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
                    ("field_size", "long"),
                    ("read_only", False),
                    ("required", False),
                    ("type", "richtext"),
                ]),
                "strong": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("label", "Copy"),
                            ("field_size", "long"),
                            ("read_only", False),
                        ]))
                    ]))
                ]),
                "weak": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([(
                        "copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("label", "Copy"),
                            ("field_size", "long"),
                            ("read_only", False),
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
                    ("required", False),
                    ("field_size", "long"),
                    ("read_only", False)

                ]),
                "con": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([
                        ("copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("field_size", "long"),
                            ("read_only", False),
                            ("label", "Copy"),

                        ]))
                    ]))
                ]),
                "pro": OrderedDict([
                    ("type", "array"),
                    ("fields", OrderedDict([
                        ("copy", OrderedDict([
                            ("type", "richtext"),
                            ("required", True),
                            ("field_size", "long"),
                            ("read_only", False),
                            ("label", "Copy"),
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
            'fields': {
                'entries': OrderedDict([
                    ('type', 'array'),
                    ('fields', OrderedDict([(
                        'title', {
                            'field_size': 'short',
                            'label': 'Title',
                            'read_only': False,
                            'required': False,
                            'type': 'richtext',
                        }
                    ), (
                        'copy_x', {
                            'field_size': 'long',
                            'label': 'Copy x',
                            'read_only': False,
                            'required': True,
                            'type': 'richtext',
                        }
                    ), (
                        'copy_y', {
                            'field_size': 'long',
                            'label': 'Copy y',
                            'read_only': False,
                            'required': True,
                            'type': 'richtext'
                        }
                    )])),
                    ('child_label', 'entry')
                ]),
                'key_x': OrderedDict([
                    ('type', 'object'),
                    ('fields', OrderedDict([(
                        'title', {
                            'field_size': 'short',
                            'label': 'Title',
                            'read_only': False,
                            'required': False,
                            'type': 'richtext'
                        }
                    ), (
                        'color', {
                            'label': 'Color',
                            'read_only': False,
                            'required': False,
                            'type': 'color',
                        }
                    ), (
                        'initial', {
                            'label': 'Initial',
                            'read_only': False,
                            'required': True,
                            'type': 'string',
                        }
                    )]))
                ]),
                'key_y': OrderedDict([
                    ('type', 'object'),
                    ('fields', OrderedDict([(
                        'title', {
                            'field_size': 'short',
                            'label': 'Title',
                            'read_only': False,
                            'required': False,
                            'type': 'richtext'
                        }
                    ), (
                        'color', {
                            'label': 'Color',
                            'read_only': False,
                            'required': False,
                            'type': 'color'
                        }
                    ), (
                        'initial', {
                            'label': 'Initial',
                            'read_only': False,
                            'required': True,
                            'type': 'string'
                        }
                    )]))
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
                "entries": [{
                    "title": "Michael Bayless",
                    "copy": "How did he do that?",
                    "image": {"id": 1}
                }, {
                    "title": "Skip Bayless",
                    "copy": "How he do that?"
                }, {
                    "copy": "AYYYY LMAO"
                }]
            }
        }

    @property
    def timeline_data(self):
        return {
            "title": "KILL ME",
            "infographic_type": InfographicType.TIMELINE,
            "data": {
                "entries": [{
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
                    "color": "#F0F8FF",
                    "initial": "A!"
                },
                "key_y": {
                    "title": "Yassss queen",
                    "color": "#F0F8EF",
                    "initial": "A!"
                },
                "entries": [{
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
