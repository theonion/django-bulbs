import datetime

from django.utils import timezone
from elastimorphic.tests.base import BaseIndexableTestCase
from model_mommy import mommy

from bulbs.promotion.models import ContentList
from bulbs.promotion.operations import InsertOperation, ReplaceOperation, LockOperation
from tests.testcontent.models import TestContentObj


class ContentListOperationsTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentListOperationsTestCase, self).setUp()
        self.content_list = ContentList.objects.create(name="homepage", length=10)
        data = []
        for i in range(10):
            data.append({"id": mommy.make(TestContentObj).pk})

        self.content_list.data = data
        self.content_list.save()

    def test_insert(self):
        new_content = mommy.make(TestContentObj)
        InsertOperation.objects.create(
            content_list=self.content_list,
            when=timezone.now() + datetime.timedelta(hours=1),
            index=0,
            content=new_content,
            lock=False
        )
        modified_list = ContentList.objects.preview("homepage", when=timezone.now() + datetime.timedelta(hours=1))
        self.assertEqual(len(modified_list), 10)  # We should only get 10 pieces of content
        self.assertEqual(len(modified_list.data), 11)  # ...though the list contains 11 items
        self.assertEqual(modified_list[0].pk, new_content.pk)

    def test_replace(self):
        new_content = mommy.make(TestContentObj)
        target = TestContentObj.objects.get(id=self.content_list[3].pk)
        ReplaceOperation.objects.create(
            content_list=self.content_list,
            when=timezone.now() + datetime.timedelta(hours=1),
            content=new_content,
            target=target
        )
        modified_list = ContentList.objects.preview("homepage", when=timezone.now() + datetime.timedelta(hours=1))
        self.assertEqual(len(modified_list), 10)
        self.assertEqual(len(modified_list.data), 10)
        self.assertEqual(modified_list[3].pk, new_content.pk)

    def test_lock(self):
        target = TestContentObj.objects.get(id=self.content_list[3].pk)
        LockOperation.objects.create(
            content_list=self.content_list,
            when=timezone.now() + datetime.timedelta(hours=1),
            target=target
        )
        modified_list = ContentList.objects.preview("homepage", when=timezone.now() + datetime.timedelta(hours=1))
        self.assertTrue(modified_list.data[3]["lock"])
