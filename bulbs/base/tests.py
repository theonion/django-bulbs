from django.utils import unittest
from django.test import TestCase as DBTestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .models import Tag, Content

class TagsTestCase(DBTestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(tag="tag1")
        self.tag2 = Tag.objects.create(tag="tag2")

        self.content_stub1 = ContentType.objects.filter(model=u"contenttype")[0]  # need some object to pretend it's content
        self.content1 = Content.objects.create(title="content1",
                                               object_id=self.content_stub1.pk,
                                               content_type=ContentType.objects.get_for_model(self.content_stub1))


        self.content_stub2 = ContentType.objects.filter(model=u"tag")[0]  # need another object to pretend it's content
        self.content2 = Content.objects.create(title="content2",
                                       object_id=self.content_stub2.pk,
                                       content_type=ContentType.objects.get_for_model(self.content_stub2))


    def test_tags(self):
        self.content1.tags.add(self.tag1)
        tagged = list(Content.objects.filter(tags__tag="tag1"))

        self.assertEqual(1, len(tagged))
        self.assertEqual(self.content1, tagged[0])

        self.content2.tags.add(self.tag1)
        tagged = list(Content.objects.filter(tags__tag="tag1"))

        self.assertEqual(2, len(tagged))
        self.assertTrue(self.content1 in tagged)
        self.assertTrue(self.content2 in tagged)

        self.content2.tags.add(self.tag2)
        tagged = list(Content.objects.filter(tags__tag="tag2"))

        self.assertEqual(1, len(tagged))
        self.assertTrue(self.content2 in tagged)

        tagged = list(Content.objects.filter(tags__tag__in=["tag1", "tag2"]).distinct())

        self.assertEqual(2, len(tagged))
        self.assertTrue(self.content1 in tagged)
        self.assertTrue(self.content2 in tagged)

