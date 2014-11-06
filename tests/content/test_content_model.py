import datetime

from django.utils import timezone
from elastimorphic.tests.base import BaseIndexableTestCase
import elasticsearch

from bulbs.content.models import Content
from tests.utils import make_content


class SerializerTestCase(BaseIndexableTestCase):
    def test_content_status(self):
        content = make_content(published=None)
        self.assertEqual(content.get_status(), "draft")

        content.published = timezone.now() - datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "final")

        content.published = timezone.now() + datetime.timedelta(hours=1)
        self.assertEqual(content.get_status(), "final")

    def test_is_published(self):
        content = make_content(published=None)
        self.assertFalse(content.is_published)

        content.published = timezone.now() - datetime.timedelta(hours=1)
        self.assertTrue(content.is_published)

        content.published = timezone.now() + datetime.timedelta(hours=1)
        self.assertFalse(content.is_published)

    def test_content_deletion(self):
        content = make_content(published=None)

        Content.search_objects.refresh()

        q = Content.search_objects.query(_id=content.id)
        self.assertEqual(q.count(), 1)

        c = Content.search_objects.es.get(
            index=content.get_index_name(),
            doc_type=content.get_mapping_type_name(),
            id=content.id)
        self.assertTrue(c.get("found"), True)

        content.delete()

        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            Content.search_objects.es.get(
                index=content.get_index_name(),
                doc_type=content.get_mapping_type_name(),
                id=content.id)

        Content.search_objects.refresh()

        q = Content.search_objects.query(_id=content.id)
        self.assertEqual(q.count(), 0)

    def test_first_image_none(self):
        content = make_content(published=None)

        content.thumbnail_override = 666

        self.assertNotEqual(content.first_image, content.thumbnail_override)

