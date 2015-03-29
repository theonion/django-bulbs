from django.utils import timezone

from elastimorphic.tests.base import BaseIndexableTestCase

from bulbs.promotion.models import PZone, PZoneHistory
from example.testcontent.models import TestContentObj
from bulbs.utils.test import make_content


class PZoneTestCase(BaseIndexableTestCase):
    def setUp(self):
        super(PZoneTestCase, self).setUp()
        self.pzone = PZone.objects.create(name="homepage")
        data = []
        for i in range(11):
            content = make_content(title="Content test #{}".format(i), )
            data.append({"id": content.pk})

        self.pzone.data = data
        self.pzone.save()

    def test_len(self):

        self.assertEqual(len(self.pzone), 10)

    def test_iter(self):
        for index, content in enumerate(self.pzone):
            self.assertEqual(self.pzone[index].title, "Content test #{}".format(index))

    def test_getitem(self):
        self.assertEqual(self.pzone[0].title, "Content test #0")
        with self.assertRaises(IndexError):
            self.pzone[10]

    def test_slice(self):
        self.assertEqual(len(self.pzone[:2]), 2)

    def test_setitem(self):
        new_content = make_content(TestContentObj)
        self.pzone[0] = new_content
        self.assertEqual(self.pzone[0].pk, new_content.pk)

        newer_content = make_content(TestContentObj)
        self.pzone[1] = newer_content.id
        self.assertEqual(self.pzone[1].pk, newer_content.pk)

    def test_contains(self):
        newer_content = make_content(TestContentObj)
        self.pzone[1] = newer_content.id

        self.assertTrue(newer_content.pk in self.pzone)
        self.assertTrue(newer_content in self.pzone)

        invisible_content = make_content(TestContentObj)
        self.assertFalse(invisible_content.pk in self.pzone)
        self.assertFalse(invisible_content in self.pzone)

    def test_history_ordering(self):
        """Test that pzone history objects come out most recently created before now first."""

        pzone_oldest = PZoneHistory.objects.create(
            pzone=self.pzone
        )
        pzone_middlest = PZoneHistory.objects.create(
            pzone=self.pzone
        )
        pzone_newest = PZoneHistory.objects.create(
            pzone=self.pzone
        )

        history = self.pzone.history.filter(date__lte=timezone.now())

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].id, pzone_newest.id)
        self.assertEqual(history[1].id, pzone_middlest.id)
        self.assertEqual(history[2].id, pzone_oldest.id)
