import datetime

from django.utils import timezone
from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.promotion.models import ContentList, InsertOperation
from tests.testcontent.models import TestContentObj


class ContentListOperationsTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentListOperationsTestCase, self).setUp()
        self.content_list = ContentList.objects.create(name="homepage")
        data = []
        for i in range(10):
            content = TestContentObj.objects.create(
                title="Content test #{}".format(i),
            )
            data.append({"id": content.pk})

        self.content_list.data = data
        self.content_list.save()

    def test_insert(self):
        content = TestContentObj.objects.create(
            title="Content test insert"
        )
        InsertOperation.objects.create(
            content_list=self.content_list,
            when=timezone.now() - datetime.timedelta(hours=1),
            index=0,
            content=content,
            lock=True
        )
        modified_list = ContentList.objects.get("homepage")
        self.assertEqual(len(modified_list.content), 10)
        self.assertEqual(modified_list.content[0].pk, content.pk)
