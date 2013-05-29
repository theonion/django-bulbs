from django.template import Context, Template
from django.template import TemplateSyntaxError
from django.core.files import File
from django.conf import settings
from django.test.client import Client

from django.test import TestCase
import requests
import StringIO
import shutil

from bulbs.images.models import Image, ImageAspectRatio


class ImageTagsTestCase(TestCase):

    def setUp(self):
        for ratio in [(16, 9), (1, 1), (3, 4)]:
            ImageAspectRatio.objects.get_or_create(width=ratio[0], height=ratio[1], slug='%sx%s' % ratio)
        image = Image.objects.create(_width=300, height=168, alt="test image", caption="test_image")
        r = requests.get("http://o.onionstatic.com/images/18/18053/original/1200.jpg")
        image_file = StringIO.StringIO()
        image_file.write(r.content)
        image.original.save(
            "1200.jpg",
            File(image_file)
        )
        image.save()

        self.context = {'image': image}

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def testImageUrlTag(self):

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/1/1x1/200_90.jpg")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" extension="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/1/1x1/200_100.png")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" extension="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/1/1x1/200_100.png")

    def testImageTag(self):
        test_template = Template("""{% load images %}{% image image 100 ratio="3x4" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, '<img src="/images/crops/1/3x4/100_90.jpg" alt="test image" />')

    def testImageCropping(self):
        client = Client()
        response = client.get('/images/crops/1/3x4/100_90.jpg')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'image/jpeg')

        response = client.get('/images/crops/1/3x4/100_90.png')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'image/png')

        response = client.get('/images/crops/1/3x4/100_47.jpg')
        self.assertEqual(response.status_code, 404)

        response = client.get('/images/crops/1/3x4/100_47.png')
        self.assertEqual(response.status_code, 404)

        response = client.get('/images/crops/1/7x9/100_90.jpg')
        self.assertEqual(response.status_code, 404)

        response = client.get('/images/crops/2/3x4/100_90.jpg')
        self.assertEqual(response.status_code, 404)
