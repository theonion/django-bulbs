from django.template import Context, Template
from django.template import TemplateSyntaxError

import unittest

from bulbs.images.models import Image, ImageAspectRatio


class ImageTagsTestCase(unittest.TestCase):

    def setUp(self):
        for ratio in [(16, 9), (1, 1), (3, 4)]:
            ImageAspectRatio.objects.get_or_create(width=ratio[0], height=ratio[1], slug='%sx%s' % ratio)
        image = Image.objects.create(_width=300, height=168, alt="test image", caption="test_image")
        self.context = {'image': image}

    def testImageUrlTag(self):

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/0/2/1x1/200_75.jpg")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/0/2/1x1/200_100.png")

        test_template = Template("""{% load images %}{% image_url image 200 ratio="1x1" format="png" %}""")
        rendered = test_template.render(test_context)
        self.assertEqual(rendered, "/images/crops/0/2/1x1/200_100.png")

    def testImageTag(self):
        test_template = Template("""{% load images %}{% image image 100 ratio="3x4" %}""")
        test_context = Context(self.context)

        rendered = test_template.render(test_context)
        self.assertEqual(rendered, '<img src="/images/crops/0/1/3x4/100_75.jpg" alt="test image" />')
