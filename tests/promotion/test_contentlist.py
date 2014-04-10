from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.content.models import Content
from bulbs.promotion.models import ContentList


from tests.testcontent.models import TestContentObj


class ContentListTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentListTestCase, self).setUp()
        self.content_list = ContentList.objects.create(name="homepage")
        data = []
        for i in range(11):
            content = TestContentObj.objects.create(
                title="Content test #{}".format(i),
            )
            data.append({"id": content.pk})

        self.content_list.data = data
        self.content_list.save()

    def test_content_list_len(self):

        self.assertEqual(len(self.content_list), 10)

    def test_content_list_iter(self):
        for index, content in enumerate(self.content_list):
            self.assertEqual(self.content_list[index].title, "Content test #{}".format(index))

    def test_content_list_getitem(self):
        self.assertEqual(self.content_list[0].title, "Content test #0")
        with self.assertRaises(IndexError):
            self.content_list[10]

    def test_content_list_setitem(self):
        new_content = Content.objects.create(title="Some dumb thing")
        self.content_list[0] = new_content
        self.assertEqual(self.content_list[0].title, "Some dumb thing")

        newer_content = Content.objects.create(title="Some other dumb thing")
        self.content_list[1] = newer_content.id
        self.assertEqual(self.content_list[1].title, "Some other dumb thing")

    def test_content_list_contains(self):
        newer_content = Content.objects.create(title="Some other dumb thing")
        self.content_list[1] = newer_content.id

        self.assertTrue(newer_content.pk in self.content_list)
        self.assertTrue(newer_content in self.content_list)

        invisible_content = Content.objects.create(title="Some mistake someone made")
        self.assertFalse(invisible_content.pk in self.content_list)
        self.assertFalse(invisible_content in self.content_list)
