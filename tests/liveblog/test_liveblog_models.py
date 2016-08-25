import six

from bulbs.utils.test import BaseIndexableTestCase, make_content

from example.testcontent.models import TestLiveBlog


class TestLiveBlogModel(BaseIndexableTestCase):

    def test_pinned_content(self):
        content = make_content()
        liveblog = TestLiveBlog.objects.create(pinned_content=content)
        self.assertEqual(liveblog.pinned_content, content)
        self.assertEqual(liveblog, content.liveblog_pinned.first())

    def test_recirc_content(self):
        content = make_content(_quantity=3)

        liveblog = TestLiveBlog.objects.create()
        liveblog.recirc_content.add(*content)
        liveblog.save()

        six.assertCountEqual(self, liveblog.recirc_content.all(), content)
        self.assertEqual(liveblog, content[0].liveblog_recirc.first())
