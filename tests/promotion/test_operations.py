import datetime

from django.utils import timezone
from elastimorphic.tests.base import BaseIndexableTestCase
from mock import patch

from bulbs.promotion.models import PZone, update_pzone
from bulbs.promotion.operations import InsertOperation, ReplaceOperation, DeleteOperation
from tests.utils import make_content


class PZoneOperationsTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(PZoneOperationsTestCase, self).setUp()
        self.pzone = PZone.objects.create(name="homepage", zone_length=10)
        data = []
        for i in range(10):
            data.append({"id": make_content().pk})

        self.pzone.data = data
        self.pzone.save()

    def test_insert_preview(self):
        """Test that an insert can be previewed."""
        test_time = timezone.now() + datetime.timedelta(hours=1)

        new_content = make_content()
        new_content.published = test_time
        new_content.save()

        InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content
        )
        # apply operations in preview mode
        modified_list = PZone.objects.preview(pk=self.pzone.id, when=test_time)
        # check that the original content hasn't changed
        self.assertEqual(len(self.pzone), 10)
        # we should only get 10 pieces of content
        self.assertEqual(len(modified_list), 10)
        # ...though the list contains 11 items
        self.assertEqual(len(modified_list.data), 11)
        # check the id of the newly inserted item
        self.assertEqual(modified_list[0].pk, new_content.pk)

    def test_ordering(self):
        one_hour = timezone.now() + datetime.timedelta(hours=1)

        test_one = make_content(published=one_hour)
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=one_hour + datetime.timedelta(hours=1),
            index=2,
            content=test_one
        )

        test_two = make_content(published=one_hour)
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=one_hour + datetime.timedelta(hours=1),
            index=3,
            content=test_two
        )

        modified_list = PZone.objects.preview(pk=self.pzone.id, when=one_hour + datetime.timedelta(hours=3))
        self.assertEqual(len(self.pzone), 10)
        self.assertEqual(len(modified_list), 10)
        self.assertEqual(len(modified_list.data), 12)
        self.assertEqual(modified_list[2].pk, test_one.pk)
        self.assertEqual(modified_list[3].pk, test_two.pk)

    def test_replace_preview(self):
        """Test that a replace can be previewed."""
        test_time = timezone.now() + datetime.timedelta(hours=1)

        new_content = make_content()
        new_content.published = test_time
        new_content.save()

        i_to_replace = 3
        ReplaceOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=new_content,
            index=i_to_replace
        )
        # apply operations in preview mode
        modified_list = PZone.objects.preview(pk=self.pzone.id, when=test_time)
        # check that we haven't changed the length of the content list
        self.assertEqual(len(modified_list), 10)
        # double check the data to ensure it wasn't modified
        self.assertEqual(len(modified_list.data), 10)
        # check that the item has been replaced at the given index
        self.assertEqual(modified_list[i_to_replace].pk, new_content.pk)

    def test_delete_preview(self):
        """Test that a delete can be previewed."""
        test_time = timezone.now() + datetime.timedelta(hours=1)
        i_of_target = 3
        DeleteOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            content=self.pzone[i_of_target]
        )
        # apply operations in preview mode
        modified_list = PZone.objects.preview(pk=self.pzone.id, when=test_time)
        # "modified" list should be one shorter
        self.assertEqual(len(modified_list), len(self.pzone) - 1)
        # ensure the target is actually removed and the space is occupied by the next item
        self.assertEqual(modified_list[i_of_target].pk, self.pzone[i_of_target + 1].pk)

    def test_apply(self):
        """Test that actually applying an operation works."""
        test_time = timezone.now() + datetime.timedelta(hours=-1)

        new_content = make_content()
        new_content.published = test_time
        new_content.save()

        InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content
        )

        # apply operation
        PZone.objects.operate_on(pk=self.pzone.id, apply=True)

        # get pzone again
        self.pzone = PZone.objects.get(id=self.pzone.id)

        # check that an item was added
        self.assertEqual(self.pzone[0].id, new_content.id)
        self.assertEqual(len(self.pzone.data), 11)

    def test_apply_with_background_task(self):
        """Test that applied function calls background task."""

        test_time = timezone.now() - datetime.timedelta(hours=1)
        new_content = make_content()
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=test_time,
            index=0,
            content=new_content
        )

        # call function with mock task method, so we can see if it was called
        with patch.object(update_pzone, 'delay') as mock_method:
            PZone.objects.applied(pk=1)

            # check that mock method was called
            self.assertTrue(mock_method.called)

    def test_prevent_insert_of_article_with_no_publish_date(self):
        """Insert operations should not complete on articles with no published date."""

        new_content = make_content()

        # article has no published date
        new_content.published = None

        # check old value at index where we're inserting
        index = 0
        old_id = self.pzone[index].id

        # attempt to insert
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() + datetime.timedelta(hours=-1),
            index=index,
            content=new_content
        )
        PZone.objects.operate_on(pk=self.pzone.id, apply=True)

        # get pzone again
        self.pzone = PZone.objects.get(id=self.pzone.id)

        # make sure the pzone has not been modified
        self.assertEqual(old_id, self.pzone[index].id)

    def test_prevent_insert_of_article_with_future_publish_date(self):
        """Insert operations should not complete on articles with a publish date in
        the future."""

        new_content = make_content()

        # article has a future published date
        new_content.published = timezone.now() + datetime.timedelta(hours=2)

        # check old value at index where we're inserting
        index = 0
        old_id = self.pzone[index].id

        # attempt to insert
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() + datetime.timedelta(hours=-1),
            index=index,
            content=new_content
        )
        PZone.objects.operate_on(pk=self.pzone.id, apply=True)

        # get pzone again
        self.pzone = PZone.objects.get(id=self.pzone.id)

        # make sure the pzone has not been modified
        self.assertEqual(old_id, self.pzone[index].id)

    def test_prevent_replace_of_article_with_no_publish_date(self):
        """Replace operations should not complete on articles with no published date."""

        new_content = make_content()

        # article has no published date
        new_content.published = None

        # check old value at index where we're inserting
        index = 0
        old_id = self.pzone[index].id

        # attempt to insert
        ReplaceOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() + datetime.timedelta(hours=-1),
            index=index,
            content=new_content
        )
        PZone.objects.operate_on(pk=self.pzone.id, apply=True)

        # get pzone again
        self.pzone = PZone.objects.get(id=self.pzone.id)

        # make sure the pzone has not been modified
        self.assertEqual(old_id, self.pzone[index].id)

    def test_prevent_replace_of_article_with_future_publish_date(self):
        """Insert operations should not complete on articles with a publish date in
        the future."""

        new_content = make_content()

        # article has a future published date
        new_content.published = timezone.now() + datetime.timedelta(hours=2)

        # check old value at index where we're inserting
        index = 0
        old_id = self.pzone[index].id

        # attempt to insert
        ReplaceOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() + datetime.timedelta(hours=-1),
            index=index,
            content=new_content
        )
        PZone.objects.operate_on(pk=self.pzone.id, apply=True)

        # get pzone again
        self.pzone = PZone.objects.get(id=self.pzone.id)

        # make sure the pzone has not been modified
        self.assertEqual(old_id, self.pzone[index].id)

    def test_prevent_insert_of_article_already_in_pzone(self):
        """Insert operations should not allow an article to be inserted that already
        exists in the pzone."""

        new_content = make_content(
            published=timezone.now() - datetime.timedelta(hours=2)
        )

        # do first operation
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() - datetime.timedelta(hours=1),
            index=0,
            content=new_content
        )

        # do another insert operation
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() - datetime.timedelta(hours=1),
            index=1,
            content=new_content
        )

        # get pzone again
        self.pzone = PZone.objects.applied(id=self.pzone.id)

        # check that state is correct
        self.assertEqual(self.pzone[0].pk, new_content.pk)
        self.assertNotEqual(self.pzone[1].pk, new_content.pk)

    def test_prevent_replace_of_article_already_in_pzone(self):
        """Replace operations should not allow an article to be inserted that already
        exists in the pzone."""

        new_content = make_content(
            published=timezone.now() - datetime.timedelta(hours=2)
        )

        # do first operation
        InsertOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() - datetime.timedelta(hours=1),
            index=0,
            content=new_content
        )

        # do another insert operation
        ReplaceOperation.objects.create(
            pzone=self.pzone,
            when=timezone.now() - datetime.timedelta(hours=1),
            index=1,
            content=new_content
        )

        # get pzone again
        self.pzone = PZone.objects.applied(id=self.pzone.id)

        # check that state is correct
        self.assertEqual(self.pzone[0].pk, new_content.pk)
        self.assertNotEqual(self.pzone[1].pk, new_content.pk)
