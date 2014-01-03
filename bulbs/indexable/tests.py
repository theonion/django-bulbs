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

        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

    def test_index_names(self):
        self.assertEqual(ParentIndexable.get_index_name(), 'testindexable_parentindexable')
        self.assertEqual(ChildIndexable.get_index_name(), 'testindexable_parentindexable')
        self.assertEqual(GrandchildIndexable.get_index_name(), 'testindexable_parentindexable')
        self.assertEqual(SeparateIndexable.get_index_name(), 'testindexable_separateindexable')

    def test_mapping_type_names(self):
        self.assertEqual(ParentIndexable.get_mapping_type_name(), 'testindexable_parentindexable')
        self.assertEqual(ChildIndexable.get_mapping_type_name(), 'testindexable_childindexable')
        self.assertEqual(GrandchildIndexable.get_mapping_type_name(), 'testindexable_grandchildindexable')
        self.assertEqual(SeparateIndexable.get_mapping_type_name(), 'testindexable_separateindexable')
        self.assertEqual(
            ParentIndexable.get_mapping_type_names(), [
                ParentIndexable.get_mapping_type_name(),
                ChildIndexable.get_mapping_type_name(),
                GrandchildIndexable.get_mapping_type_name(),
            ]
        )
        self.assertEqual(
            SeparateIndexable.get_mapping_type_names(), [
                SeparateIndexable.get_mapping_type_name(),
            ]
        )

    def test_get_index_mappings(self):
        pass

    def test_primary_key_name_is_correct(self):
        a, b, c = [klass.get_mapping().values()[0]['_id']['path'] for klass in (
            ParentIndexable, ChildIndexable, GrandchildIndexable
        )]
        self.assertEqual(a, b)
        self.assertEqual(b, c)

    def test_search(self):
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(bar=69).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="Fighters").count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(baz__lte=datetime.datetime.now()).count(), 1)

        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

    def test_instanceof(self):
        self.assertEqual(ParentIndexable.search_objects.s().instanceof(ParentIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instanceof(ChildIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instanceof(GrandchildIndexable, exact=True).count(), 1)

        self.assertEqual(ParentIndexable.search_objects.s().instanceof(ParentIndexable).count(), 3)
        self.assertEqual(ParentIndexable.search_objects.s().instanceof(ChildIndexable).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.s().instanceof(GrandchildIndexable).count(), 1)

    def test_model_results(self):
        qs = ParentIndexable.search_objects.s().full()
        for obj in qs:
            self.assertTrue(obj.__class__ in [ParentIndexable, ChildIndexable, GrandchildIndexable])

        self.assertEqual(len(qs[:2]), 2)

    def test_s_all_respects_slicing(self):
        s = ParentIndexable.search_objects.s()
        num_s = s.count()
        self.assertEqual(len(s), num_s)
        sliced = s[1:2]
        self.assertEqual(len(sliced.all()), 1)

    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        es.delete_index(ParentIndexable.get_index_name())
        es.delete_index(SeparateIndexable.get_index_name())
