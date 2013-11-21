import os
import shutil
import random
import json
import socket

from django.template import Context, Template
from django.template import TemplateSyntaxError
from django.core.files import File
from bulbs.images.conf import settings
from django.test.client import Client
from django.db import models
from django.test import TestCase
from django.db.models.fields.files import FieldFile

from httmock import urlmatch, HTTMock

from bulbs.images.fields import RemoteImageField


APP_DIR = os.path.dirname(__file__)


@urlmatch(path='/api/new')
def betty_mock(url, request):
    return {'status_code': 201, 'content': json.dumps({"id": 10})}


class TestModel(models.Model):
    image = RemoteImageField()

class ImageTagsTestCase(TestCase):

    def setUp(self):
        # with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
        self.test = TestModel()
        self.test.image = self.test.image.field.attr_class(self.test, self.test.image.field, '666')
        self.test.save()
        self.context = {'test': self.test}

        self.test_empty = TestModel()
        self.test_empty.save()

    def test_image_field(self):
        settings.BETTY_CROPPER = {
            'ADMIN_URL': 'http://localhost:8698',
            'PUBLIC_URL': 'http://localhost:8698',
        }
        with HTTMock(betty_mock):
            with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
                test = TestModel()
                test.image = File(lenna)
                test.save()
                self.assertEqual(test.image.name, "10")


    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_image_url_tag(self):

        test_template = Template("""{% load images %}{% cropped_url test.image "1x1" 200 %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8698/666/1x1/200.jpg")

        test_template = Template("""{% load images %}{% cropped_url test.image "1x1" 200 format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8698/666/1x1/200.png")

        test_template = Template("""{% load images %}{% cropped_url test.image "1x1" 200 format="png" %}""")
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
