import datetime

from django.db import models
from django.test import TestCase
from django.conf import settings

from bulbs.indexable import PolymorphicIndexable, SearchManager, create_polymorphic_indexes

from elasticutils.contrib.django import get_es

from polymorphic import PolymorphicModel


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

    def test_indexing(self):
        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))

        es = get_es(urls=settings.ES_URLS)
        es.refresh(ParentIndexable.get_index_name())

        self.assertEqual(ParentIndexable.search.query(bar=69).count(), 2)
        self.assertEqual(ParentIndexable.search.query(foo__match="Fighters").count(), 3)
        self.assertEqual(ParentIndexable.search.query(baz__lte=datetime.datetime.now()).count(), 1)

    def test_simple(self):
        self.assertEqual(ParentIndexable.get_index_name(), 'indexable_parentindexable')
        self.assertEqual(ChildIndexable.get_index_name(), 'indexable_parentindexable')
        self.assertEqual(GrandchildIndexable.get_index_name(), 'indexable_parentindexable')

    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        es.delete_index(ParentIndexable.get_index_name())