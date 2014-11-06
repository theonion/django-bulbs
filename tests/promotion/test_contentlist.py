from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.promotion.models import ContentList
from tests.testcontent.models import TestContentObj
from tests.utils import make_content


class ContentListTestCase(BaseIndexableTestCase):
    def setUp(self):
        super(ContentListTestCase, self).setUp()
        self.content_list = ContentList.objects.create(name="homepage")
        data = []
        for i in range(11):
            content = make_content(title="Content test #{}".format(i), )
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

    def test_contet_list_slice(self):
        self.assertEqual(len(self.content_list[:2]), 2)

    def test_content_list_setitem(self):
        new_content = make_content(TestContentObj)
        self.content_list[0] = new_content
        self.assertEqual(self.content_list[0].pk, new_content.pk)

        newer_content = make_content(TestContentObj)
        self.content_list[1] = newer_content.id
        self.assertEqual(self.content_list[1].pk, newer_content.pk)

    def test_content_list_contains(self):
        newer_content = make_content(TestContentObj)
        self.content_list[1] = newer_content.id

        self.assertTrue(newer_content.pk in self.content_list)
        self.assertTrue(newer_content in self.content_list)

        invisible_content = make_content(TestContentObj)
        self.assertFalse(invisible_content.pk in self.content_list)
        self.assertFalse(invisible_content in self.content_list)
