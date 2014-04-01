import datetime

from django.utils import timezone

from elastimorphic.tests.base import BaseIndexableTestCase

from tests.testcontent.models import TestContentObj


class SerializerTestCase(BaseIndexableTestCase):

    def test_content_status(self):

        content = TestContentObj.objects.create(
            title="Ubpublished article"
        )
        self.assertEqual(content.get_status(), "draft")

        content.published = timezone.now() - datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "published")

        content.published = timezone.now() + datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "scheduled")
