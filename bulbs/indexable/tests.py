import datetime

from django.db import models
from django.test import TestCase
from django.conf import settings

from bulbs.indexable import PolymorphicIndexable, SearchManager, create_polymorphic_indexes

from elasticutils.contrib.django import get_es

from polymorphic import PolymorphicModel

class SeparateIndexable(PolymorphicIndexable, PolymorphicModel):
    junk = models.CharField(max_length=255)

    search = SearchManager()


class ParentIndexable(PolymorphicIndexable, PolymorphicModel):
    foo = models.CharField(max_length=255)

    search = SearchManager()

    def extract_document(self):
        doc = super(ParentIndexable, self).extract_document()
        doc['foo'] = self.foo
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(ParentIndexable, cls).get_mapping_properties()
        properties.update({
            "foo": {"type": "string"}
        })
        return properties


class ChildIndexable(ParentIndexable):
    bar = models.IntegerField()

    def extract_document(self):
        doc = super(ChildIndexable, self).extract_document()
        doc['bar'] = self.bar
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(ChildIndexable, cls).get_mapping_properties()
        properties.update({
            "bar": {"type": "integer"}
        })
        return properties


class GrandchildIndexable(ChildIndexable):
    baz = models.DateField()

    def extract_document(self):
        doc = super(GrandchildIndexable, self).extract_document()
        doc['baz'] = self.baz
        return doc

    @classmethod
    def get_mapping_properties(cls):
        properties = super(GrandchildIndexable, cls).get_mapping_properties()
        properties.update({
            "baz": {"type": "date"}
        })
        return properties


class IndexableTestCase(TestCase):

    def setUp(self):
        create_polymorphic_indexes(None)

        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))
        
        SeparateIndexable.objects.create(junk="Testing")

        ParentIndexable.search.refresh()
        SeparateIndexable.search.refresh()


    def test_index_names(self):
        self.assertEqual(ParentIndexable.get_index_name(), 'indexable_parentindexable')
        self.assertEqual(ChildIndexable.get_index_name(), 'indexable_parentindexable')
        self.assertEqual(GrandchildIndexable.get_index_name(), 'indexable_parentindexable')

        self.assertEqual(SeparateIndexable.get_index_name(), 'indexable_separateindexable')

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

    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        es.delete_index(ParentIndexable.get_index_name())