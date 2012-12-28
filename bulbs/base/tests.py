from django.utils import unittest
from django.test import TestCase as DBTestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .models import Tag, Content

class TagsTestCase(DBTestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(tag="tag1")
        self.tag2 = Tag.objects.create(tag="tag2")

        generic_stub_content = ContentType.objects.filter(model=u"contenttype")[0]  # need some object to pretend its content

        self.content_stub1 = generic_stub_content
        self.content1 = Content.objects.create(title="content1",
                                               object_id=self.content_stub1.pk,
                                               content_type=ContentType.objects.get_for_model(self.content_stub1))


    def test_foo(self):
        self.assertEqual(1, 1)

