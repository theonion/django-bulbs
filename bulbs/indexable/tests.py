from __future__ import absolute_import

import datetime

from django.test import TestCase
from django.conf import settings

from elasticutils.contrib.django import get_es

from tests.testindexable.models import ParentIndexable, ChildIndexable, GrandchildIndexable, SeparateIndexable

class IndexableTestCase(TestCase):

    def setUp(self):
        # create_polymorphic_indexes(ParentIndexable)
        # create_polymorphic_indexes(SeparateIndexable)

        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))
        
        SeparateIndexable.objects.create(junk="Testing")

        ParentIndexable.search.refresh()
        SeparateIndexable.search.refresh()


    def test_index_names(self):
        self.assertEqual(ParentIndexable.get_index_name(), 'testindexable_parentindexable')
        self.assertEqual(ChildIndexable.get_index_name(), 'testindexable_parentindexable')
        self.assertEqual(GrandchildIndexable.get_index_name(), 'testindexable_parentindexable')

        self.assertEqual(SeparateIndexable.get_index_name(), 'testindexable_separateindexable')

    def test_search(self):

        self.assertEqual(ParentIndexable.search.s().count(), 3)
        self.assertEqual(ParentIndexable.search.query(bar=69).count(), 2)
        self.assertEqual(ParentIndexable.search.query(foo__match="Fighters").count(), 3)
        self.assertEqual(ParentIndexable.search.query(baz__lte=datetime.datetime.now()).count(), 1)

        self.assertEqual(SeparateIndexable.search.s().count(), 1)

    def test_instanceof(self):
        self.assertEqual(ParentIndexable.search.s().instanceof(ParentIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search.s().instanceof(ChildIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search.s().instanceof(GrandchildIndexable, exact=True).count(), 1)

        self.assertEqual(ParentIndexable.search.s().instanceof(ParentIndexable).count(), 3)
        self.assertEqual(ParentIndexable.search.s().instanceof(ChildIndexable).count(), 2)
        self.assertEqual(ParentIndexable.search.s().instanceof(GrandchildIndexable).count(), 1)

    def test_model_Results(self):
        qs = ParentIndexable.search.s().full()
        for obj in qs:
            self.assertTrue(obj.__class__ in [ParentIndexable, ChildIndexable, GrandchildIndexable])

        self.assertEqual(len(qs[:2]), 2)

    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        es.delete_index(ParentIndexable.get_index_name())
        es.delete_index(SeparateIndexable.get_index_name())