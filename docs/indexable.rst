==========
 Indexable
==========

.. contents::
   :local:

Overview
========

The ``indexable`` app allows for easy indexing and searching of `django-polymorphic`_ models, using `Elasticsearch`_.

Setup
=====

In order to use the indexable functionality, you'll have to add ``bulbs.indexable`` to your ``INSTALLED_APPS``, as well adding an ``ES_URLS`` list to your Django settings. By default, ES_URLS is set as::

    ES_URLS = ["http://localhost:9200"]

Usage
=====

A mixin, `PolymophicIndexable`, needs added to your Django model.

For example::

    from django.db import models
    from bulbs.indexable import PolymorphicIndexable, SearchManager
    from polymorphic import PolymorphicModel


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

API
===
.. autoclass:: bulbs.indexable.PolymorphicIndexable
   :members: