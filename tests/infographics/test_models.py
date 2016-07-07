from django.db import connection

from rest_framework.serializers import ValidationError

from bulbs.infographics.models import BaseInfographic, InfographicType
from bulbs.utils.test import BaseIndexableTestCase


class BaseInfographicTestCase(BaseIndexableTestCase):

    def test_infographic_data_is_jsonb(self):
        """Asserts that the `BaseInfographic.data` field is of type `jsonb`."""
        field = BaseInfographic._meta.get_field("data")
        self.assertEqual(field.db_type(connection), "jsonb")

    def test_create_success(self):
        infographic = BaseInfographic.objects.create(
            title="A GOOD BOYS ADVENTURE",
            infographic_type=InfographicType.LIST,
            data={
                "is_numbered": True,
                "entries": [{
                    "title": "Michael Bayless",
                    "copy": "How did he do that?",
                    "image": {"id": 1}
                }]
            }
        )
        db_infographic = BaseInfographic.objects.get(pk=infographic.pk)
        self.assertEqual(db_infographic.pk, infographic.pk)

    def test_create_missing_field(self):
        with self.assertRaises(ValidationError):
            BaseInfographic.objects.create(
                title="A GOOD BOYS ADVENTURE",
                infographic_type=InfographicType.LIST,
                data=[{
                    "is_numbered": True,
                    "copy": "How did he do that?",
                    "image": {"id": 1}
                }]
            )

    def test_create_wrong_type(self):
        with self.assertRaises(ValidationError):
            BaseInfographic.objects.create(
                title="A GOD BOY ADVENTURE",
                infographic_type=InfographicType.LIST,
                data=[{
                    "title": "It me.",
                    "is_numbered": "Tru",
                    "copy": "Who dat?",
                    "image": {"id": 1}
                }]
            )

    def test_timeline_validator(self):
        BaseInfographic.objects.create(
            title="A GOD BOY ADVENTURE",
            infographic_type=InfographicType.TIMELINE,
            data={
                "entries": [{
                    "title": "Sickass",
                    "copy": "heya",
                    "image": {"id": 50}
                }]
            }
        )

    def test_get_infographic_type_name(self):
        instance = BaseInfographic.objects.create(
            title="A GOD BOY ADVENTURE",
            infographic_type=InfographicType.TIMELINE,
            data={
                "entries": [{
                    "title": "Sickass",
                    "copy": "heya",
                    "image": {"id": 50}
                }]
            }
        )
        self.assertEqual(instance.get_infographic_type_name(), "Timeline")
