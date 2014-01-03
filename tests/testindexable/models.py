from django.db import models

from bulbs.indexable import PolymorphicIndexable, SearchManager

from polymorphic import PolymorphicModel

class SeparateIndexable(PolymorphicIndexable, PolymorphicModel):
    junk = models.CharField(max_length=255)

    search_objects = SearchManager()


class ParentIndexable(PolymorphicIndexable, PolymorphicModel):
    foo = models.CharField(max_length=255)

    search_objects = SearchManager()

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