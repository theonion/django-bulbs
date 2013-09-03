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

from pretenders.client.http import HTTPMock
from pretenders.constants import FOREVER

from bulbs.images.fields import RemoteImageField


APP_DIR = os.path.dirname(__file__)


class TestModel(models.Model):
    image = RemoteImageField()

class ImageTagsTestCase(TestCase):

    def setUp(self):
        with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
            test = TestModel()
            test.image = File(lenna, name="666")
        self.context = {'image': test.image}

    def test_image_field(self):
        try:
            mock_betty_admin = HTTPMock('localhost', 9999, timeout=20, name="betty_admin")
            mock_betty_public = HTTPMock('localhost', 9999, timeout=20, name="betty_public")
        except socket.error:
            # Skip this test, we don't have a working server.
            return

        settings.BETTY_CROPPER = {
            'ADMIN_URL': 'http://localhost:9999%s' % mock_betty_admin.pretender_details.get('path'),
            'PUBLIC_URL': 'http://localhost:9999%s' % mock_betty_public.pretender_details.get('path')
        }
        mock_betty_admin.when("POST /api/new").reply(json.dumps({"id": 10}), status=201, times=FOREVER)

        with open(os.path.join(APP_DIR, "test_images", "Lenna.png"), "r") as lenna:
            test = TestModel()
            test.image = File(lenna)
            test.save()
            self.assertEqual(test.image.name, "10")


    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def testImageUrlTag(self):

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8888/666/1x1/200.jpg")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8888/666/1x1/200.png")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "http://localhost:8888/666/1x1/200.png")

    def testImageTag(self):
        test_template = Template("""{% load images %}{% image image 100 ratio="3x4" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, '<img src="http://localhost:8888/666/3x4/100.jpg" />')
