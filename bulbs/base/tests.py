import rawes
import copy

from django.test import TestCase as DBTestCase
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.conf import settings

from bulbs.base.models import Tag, Content
try:
    from testapp.models import TestContentObj
except:
    raise ImportError("Something with your test app isn't configured correctly")


class ESTestCase(DBTestCase):

    def setUp(self):
        # Create index, if necessary
        call_command('sync_es')
        self.es = rawes.Elastic(**settings.ES_SERVER)

    def tearDown(self):
        server_conf = copy.deepcopy(settings.ES_SERVER)
        index_name = server_conf['path']
        del server_conf['path']
        es = rawes.Elastic(**server_conf)
        es.delete(index_name)


class TagsTestCase(ESTestCase):

    def setUp(self):
        super(TagsTestCase, self).setUp()
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
        test_obj1 = TestContentObj.objects.create(title="content1",
                                                    field1="myfield1",
                                                    field2="myfield2")

        test_obj2 = TestContentObj.objects.create(title="content2",
                                                    field1="mysecondfield1",
                                                    field2="mysecondfield2")

        self.assertEqual(0, Content.objects.tagged_as("tag1").count())

        test_obj1.content.tags.add(self.tag1)
        self.assertEqual(1, Content.objects.tagged_as("tag1").count())

        test_obj2.content.tags.add(self.tag1)
        self.assertEqual(2, Content.objects.tagged_as("tag1").count())

        test_obj2.content.tags.add(self.tag2)
        self.assertEqual(1, Content.objects.tagged_as("tag2").count())
        self.assertEqual(2, Content.objects.tagged_as("tag1", "tag2").count())
        self.assertEqual(1, Content.objects.tagged_as("tag1", "tag2").filter(title="content1").count())

    def test_only_type_manager(self):
        test_obj1 = TestContentObj.objects.create(title="content1",
                                                    field1="myfield1",
                                                    field2="myfield2")

        self.assertEquals([test_obj1.content], list(Content.objects.only_type(TestContentObj)))
        self.assertEquals([test_obj1.content], list(Content.objects.only_type(test_obj1)))


class ContentMixinTestCase(ESTestCase):

    def test_content_url(self):
        TestContentObj.objects.create(title="content_title",
                              field1="myfield1",
                              field2="myfield2")
        content_object = Content.objects.get()
        self.assertEquals(content_object.get_absolute_url(), "/testobject/%s" % content_object.pk)

    def test_content_property(self):
        test_obj1 = TestContentObj.objects.create(title="content1",
                                                    field1="myfield1",
                                                    field2="myfield2")

        self.assertEquals(test_obj1.content.title, "content1")

    def test_create_content(self):
        TestContentObj.objects.create(title="content_title",
                                      field1="myfield1",
                                      field2="myfield2")

        self.assertEquals(TestContentObj.objects.get().field1, "myfield1")
        self.assertEquals(TestContentObj.objects.get().field2, "myfield2")
        self.assertEquals(TestContentObj.objects.get().content.title, "content_title")
