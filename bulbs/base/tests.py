from django.utils import unittest
from django.test import TestCase as DBTestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .models import Tag, Content, TestContentObj

class TagsTestCase(DBTestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(name="tag1")
        self.tag2 = Tag.objects.create(name="tag2")

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
        tagged = list(Content.objects.filter(tags__name="tag1"))

        self.assertEqual(1, len(tagged))
        self.assertEqual(self.content1, tagged[0])

        self.content2.tags.add(self.tag1)
        tagged = list(Content.objects.filter(tags__name="tag1"))

        self.assertEqual(2, len(tagged))
        self.assertTrue(self.content1 in tagged)
        self.assertTrue(self.content2 in tagged)

        self.content2.tags.add(self.tag2)
        tagged = list(Content.objects.filter(tags__name="tag2"))

        self.assertEqual(1, len(tagged))
        self.assertTrue(self.content2 in tagged)

        tagged = list(Content.objects.filter(tags__name__in=["tag1", "tag2"]).distinct())

        self.assertEqual(2, len(tagged))
        self.assertTrue(self.content1 in tagged)
        self.assertTrue(self.content2 in tagged)


    def test_tag_manager(self):
        test_obj1 = TestContentObj.objects.create(field1="myfield1",
                                                  field2="myfield2")
        test_obj1_content = Content.objects.create(object_id=test_obj1.pk,
                                                   content_type=ContentType.objects.get_for_model(test_obj1),
                                                   title="content1")

        test_obj2 = TestContentObj.objects.create(field1="mysecondfield1",
                                                  field2="mysecondfield2")
        test_obj2_content = Content.objects.create(object_id=test_obj2.pk,
                                                   content_type=ContentType.objects.get_for_model(test_obj2),
                                                   title="content2")

        self.assertEqual(0, Content.objects.tagged_as("tag1").count())

        test_obj1_content.tags.add(self.tag1)
        self.assertEqual(1, Content.objects.tagged_as("tag1").count())

        test_obj2_content.tags.add(self.tag1)
        self.assertEqual(2, Content.objects.tagged_as("tag1").count())

        test_obj2_content.tags.add(self.tag2)
        self.assertEqual(1, Content.objects.tagged_as("tag2").count())
        self.assertEqual(2, Content.objects.tagged_as("tag1", "tag2").count())
        self.assertEqual(1, Content.objects.tagged_as("tag1", "tag2").filter(title="content1").count())



class ContentMixinTestCase(DBTestCase):

    def test_content_property(self):
        test_obj1 = TestContentObj.objects.create(field1="myfield1",
                                                  field2="myfield2")
        test_obj1_content = Content.objects.create(object_id=test_obj1.pk,
                                                   content_type=ContentType.objects.get_for_model(test_obj1),
                                                   title="content1")

        self.assertEquals(test_obj1.content.title, "content1")


    def test_content_property_raises_obj_not_exist(self):
        test_obj1 = TestContentObj.objects.create(field1="myfield1",
                                                  field2="myfield2")
        self.assertRaises(Content.DoesNotExist, lambda: test_obj1.content)


    def test_create_content(self):
        TestContentObj.create_content(content__title="content_title",
                                      field1="myfield1",
                                      field2="myfield2")

        self.assertEquals(TestContentObj.objects.get().field1, "myfield1")
        self.assertEquals(TestContentObj.objects.get().field2, "myfield2")
        self.assertEquals(TestContentObj.objects.get().content.title, "content_title")