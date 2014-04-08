from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.promotion.models import ContentList

from tests.testcontent.models import TestContentObj


class ContentListTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def test_content_list(self):
        content_list = ContentList.objects.create(name="homepage")
        content_ids = []
        for i in range(10):
            content = TestContentObj.objects.create(
                title="Content test #{}".format(i),
            )
            content_ids.append(content.pk)

        content_list.content_ids = content_ids
        content_list.save()

        self.assertEqual(len(content_list.content), 10)
        for index, content in enumerate(content_list.content):
            self.assertEqual(content.title, "Content test #{}".format(index))
