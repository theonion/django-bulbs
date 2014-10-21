import datetime

from django.utils import timezone

from elastimorphic.tests.base import BaseIndexableTestCase
import elasticsearch

from tests.testcontent.models import TestContentObj


class SerializerTestCase(BaseIndexableTestCase):

    def test_content_status(self):

        content = TestContentObj.objects.create(
            title="Unpublished article"
        )
        self.assertEqual(content.get_status(), "draft")

        content.published = timezone.now() - datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "final")

        content.published = timezone.now() + datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "final")

    def test_is_published(self):
        content = TestContentObj.objects.create(
            title="Unpublished article"
        )
        self.assertFalse(content.is_published)

        content.published = timezone.now() - datetime.timedelta(hours=1)
        self.assertTrue(content.is_published)

        content.published = timezone.now() + datetime.timedelta(hours=1)
        self.assertFalse(content.is_published)

    def test_content_deletion(self):
        content = TestContentObj.objects.create(
            title="Some article"
        )

        TestContentObj.search_objects.refresh()

        q = TestContentObj.search_objects.query(_id=content.id)
        self.assertEqual(q.count(), 1)

        c = TestContentObj.search_objects.es.get(
            index=content.get_index_name(),
            doc_type=TestContentObj.get_mapping_type_name(),
            id=content.id)
        self.assertTrue(c.get("found"), True)

        content.delete()

        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            TestContentObj.search_objects.es.get(
                index=content.get_index_name(),
                doc_type=TestContentObj.get_mapping_type_name(),
                id=content.id)

        TestContentObj.search_objects.refresh()

        q = TestContentObj.search_objects.query(_id=content.id)
        self.assertEqual(q.count(), 0)

    def test_first_image_none(self):

        content = TestContentObj.objects.create(
            title="Some article"
        )

        content.thumbnail_override = 666

        self.assertNotEqual(content.first_image, content.thumbnail_override)

