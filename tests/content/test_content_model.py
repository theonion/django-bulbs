import datetime

from django.utils import timezone
from bulbs.utils.test import BaseIndexableTestCase
import elasticsearch

from bulbs.content.models import Content
from bulbs.utils.test import make_content


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

        response = self.es.get(
            index=content.mapping.index,
            doc_type=content.mapping.doc_type,
            id=content.id)
        assert response["found"] is True

        content.delete()

        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            response = self.es.get(
                index=content.mapping.index,
                doc_type=content.mapping.doc_type,
                id=content.id)

        Content.search_objects.refresh()

    def test_first_image_none(self):
        content = make_content(published=None)

        content.thumbnail_override = 666

        self.assertNotEqual(content.first_image, content.thumbnail_override)
