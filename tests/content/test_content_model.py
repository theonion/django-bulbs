import datetime

from django.utils import timezone

import elasticsearch

from bulbs.content.models import Content
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class ContentModelTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentModelTestCase, self).setUp()
        self.default_data = {"foo": "Mike sucks."}

    def test_get_template_name_default(self):
        obj = TestContentObj.objects.create(**self.default_data)
        self.assertIsNone(obj.get_template_name())

    def test_get_template_name(self):
        self.default_data.update({"template_choice": 1})
        obj = TestContentObj.objects.create(**self.default_data)
        self.assertEqual(obj.get_template_name(), "special_coverage/landing.html")


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
        content.__class__.search_objects.refresh()

        index = content.__class__.search_objects.mapping.index
        doc_type = content.__class__.search_objects.mapping.doc_type

        response = self.es.get(
            index=index,
            doc_type=doc_type,
            id=content.id)
        assert response["found"] is True

        content.delete()

        with self.assertRaises(elasticsearch.exceptions.NotFoundError):
            response = self.es.get(
                index=index,
                doc_type=doc_type,
                id=content.id)

        Content.search_objects.refresh()

    def test_first_image_none(self):
        content = make_content(published=None)

        content.thumbnail_override = 666

        self.assertNotEqual(content.first_image, content.thumbnail_override)
