from django.db import connection

from bulbs.infographics.models import BaseInfographic
from bulbs.utils.test import BaseIndexableTestCase


class BaseInfographicTestCase(BaseIndexableTestCase):

    def test_infographic_data_is_jsonb(self):
        """Asserts that the `BaseInfograhpic.data` field is of type `jsonb`."""
        jsonfield = BaseInfographic._meta.get_field("data")
        self.assertEqual(jsonfield.db_type(connection), "jsonb")
