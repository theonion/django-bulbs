import os
import shutil
import json

from django.template import Context, Template
from bulbs.images.conf import settings
from django.db import models
from django.test import TestCase

from httmock import urlmatch, HTTMock

from bulbs.images.fields import RemoteImageField, RemoteImageSerializer


APP_DIR = os.path.dirname(__file__)


@urlmatch(path='/api/new')
def betty_mock(url, request):
    return {'status_code': 201, 'content': json.dumps({"id": 10})}


class TestModel(models.Model):
    image = RemoteImageField()


class ImageCaptionTestCase(TestCase):

    def test_caption(self):
        test = TestModel()
        test.image = test.image.field.attr_class(test, test.image.field, '666')
        test.save()

        self.assertIsNone(test.image.caption)
        test.image.caption = "Testing caption"
        self.assertEqual(test.image.caption, "Testing caption")
        self.assertIsNone(test.image.alt)
        self.assertEqual(test.image.id, "666")
        test.save()

        test = TestModel.objects.get(id=test.id)
        self.assertEqual(test.image.caption, "Testing caption")
        self.assertIsNone(test.image.alt)
        self.assertEqual(test.image.id, "666")

    def test_alt(self):
        test = TestModel()
        test.image = test.image.field.attr_class(test, test.image.field, '69')
        test.save()

        self.assertIsNone(test.image.alt)
        test.image.alt = "Some snarky shit"
        self.assertIsNone(test.image.caption)
        self.assertEqual(test.image.alt, "Some snarky shit")
        self.assertEqual(test.image.id, "69")
        test.save()

        test = TestModel.objects.get(id=test.id)
        self.assertIsNone(test.image.caption)
        self.assertEqual(test.image.alt, "Some snarky shit")
        self.assertEqual(test.image.id, "69")

    def test_import(self):
        test = TestModel()
        test.image = test.image.field.attr_class(test, test.image.field, '{"id": "69"}')
        test.save()

        self.assertIsNone(test.image.alt)
        test.image.alt = "Some snarky shit"
        self.assertIsNone(test.image.caption)
        self.assertEqual(test.image.alt, "Some snarky shit")
        self.assertEqual(test.image.id, "69")
        test.save()

        test = TestModel.objects.get(id=test.id)
        self.assertIsNone(test.image.caption)
        self.assertEqual(test.image.alt, "Some snarky shit")
        self.assertEqual(test.image.id, "69")


class ImageSerializationTestCase(TestCase):

    def test_from_native(self):
        test = TestModel()
        test.image = test.image.field.attr_class(test, test.image.field, '{"id": "69"}')
        test.save()
        serializer = RemoteImageSerializer()
        self.assertEqual(serializer.to_native(test.image).get('id'), '69')

    def test_to_native(self):
        pass


class ImageTagsTestCase(TestCase):

    def setUp(self):
        # with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
        self.test = TestModel()
        self.test.image = self.test.image.field.attr_class(self.test, self.test.image.field, '666')
        self.test.save()
        self.context = {'test': self.test}

        self.test_empty = TestModel()
        self.test_empty.save()

    # def test_image_field(self):
    #     settings.BETTY_CROPPER = {
    #         'ADMIN_URL': 'http://localhost:8698',
    #         'PUBLIC_URL': 'http://localhost:8698',
    #     }
    #     with HTTMock(betty_mock):
    #         with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
    #             test = TestModel()
    #             test.image = File(lenna)
    #             test.save()
    #             self.assertEqual(test.image.name, "10")

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_image_url_tag(self):

        test_template = Template("""{% load images %}{% cropped_url test.image "1x1" 200 %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8698/666/1x1/200.jpg")

        test_template = Template(
            """{% load images %}{% cropped_url test.image "1x1" 200 format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8698/666/1x1/200.png")

        test_template = Template(
            """{% load images %}{% cropped_url test.image "1x1" 200 format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8698/666/1x1/200.png")

    def test_image_tag(self):
        test_template = Template("""{% load images %}{% cropped test.image "3x4" 100 %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, '<img src="http://localhost:8698/666/3x4/100.jpg" />')

    def test_default_image(self):
        test_template = Template("""{% load images %}{% cropped test_empty.image "3x4" 100 %}""")
        test_context = Context({'test_empty': self.test_empty})

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, '<img src="http://localhost:8698/1234/5/3x4/100.jpg" />')
