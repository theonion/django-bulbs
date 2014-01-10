from __future__ import absolute_import

import datetime

from django.test import TestCase
from django.core.management import call_command

from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from bulbs.indexable.models import polymorphic_indexable_registry
from bulbs.indexable.conf import settings

from tests.testindexable.models import ParentIndexable, ChildIndexable, GrandchildIndexable, SeparateIndexable


class BaseIndexableTestCase(TestCase):
    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        for base_class in polymorphic_indexable_registry.families.keys():
            try:
                es.delete_index(base_class.get_index_name())
            except ElasticHttpNotFoundError:
                pass


class IndexableTestCase(BaseIndexableTestCase):

    def setUp(self):
        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))

        SeparateIndexable.objects.create(junk="Testing")

        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

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


class BulkIndexTestCase(BaseIndexableTestCase):

    def test_management_command(self):
        ParentIndexable(foo="Fighters").save(index=False)
        ChildIndexable(foo="Fighters", bar=69).save(index=False)

        GrandchildIndexable(
            foo="Fighters",
            bar=69,
            baz=datetime.datetime.now() - datetime.timedelta(hours=1)
        ).save(index=False)

        SeparateIndexable(junk="Testing").save(index=False)

        # Let's make sure that nothing is indexed yet.
        self.assertEqual(ParentIndexable.search_objects.s().count(), 0)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 0)

        # Now that everything has been made, let's try a bulk_index.
        call_command('bulk_index')
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

        # Let's make sure that everything has the right counts
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

        # Let's add another one, make sure the counts are right.
        ParentIndexable(foo="Mr. T").save(index=False)
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        call_command('bulk_index')
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # Let's fuck up some data in ES.
        obj = ParentIndexable.objects.all()[0]
        es = get_es(urls=settings.ES_URLS)
        doc = obj.extract_document()
        doc["foo"] = "DATA FUCKERS"
        es.update(obj.get_index_name(), obj.get_mapping_type_name(), obj.id, doc=doc, upsert=doc, refresh=True)

        # Make sure the bad data works
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA FUCKERS").count(), 1)
        call_command('bulk_index')
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA FUCKERS").count(), 0)

        # Let's delete an item from the db.
        obj = ParentIndexable.objects.all()[0]
        obj.delete()

        # Make sure the count is the same
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This shoulnd't remove the item
        call_command('bulk_index')
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This should
        call_command('bulk_index', purge=True)
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)


class TestPolymorphicIndexableRegistry(TestCase):
    def test_registry_has_models(self):
        self.assertTrue(polymorphic_indexable_registry.all_models)
        self.assertTrue(polymorphic_indexable_registry.families)
        types = polymorphic_indexable_registry.get_doctypes(ParentIndexable)
        desired_classes = set([ParentIndexable, ChildIndexable, GrandchildIndexable])
        result_classes = set()
        for name, klass in types.items():
            result_classes.add(klass)
        self.assertEqual(desired_classes, result_classes)

