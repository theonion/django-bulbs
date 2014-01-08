"""
The ``indexable`` app allows for easy indexing and searching of `django-polymorphic <https://django-polymorphic.readthedocs.org>`_ models, using `Elasticsearch <http://www.elasticsearch.org>`_.

Setup
=====

In order to use the indexable functionality, you'll have to add ``bulbs.indexable`` to your ``INSTALLED_APPS``, as well adding an ``ES_URLS`` list to your Django settings. By default, ES_URLS is set as::

    ES_URLS = ["http://localhost:9200"]

You'll also need to have some models that extend from `PolymorphicIndexable`. After that, a simple `syncdb` command will create indexes and mappings for you.
"""

from .indexable import PolymorphicIndexable, SearchManager