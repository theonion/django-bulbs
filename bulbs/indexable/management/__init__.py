"""This module allows us to automatically create mappings and indexes for Polymorphic models
after syncdb runs. The way that this works is a little fragile, but better than having to connect a signal in each of your apps."""

import importlib

from django.db import models
from django.conf import settings
from django.db.models.signals import post_syncdb
from django.db.models.loading import get_models

from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from bulbs.indexable import PolymorphicIndexable
from bulbs.indexable.models import polymorphic_indexable_registry


# Default ES Settings--should probably be grabbed from the django settings?
ES_SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": ["asciifolding", "lowercase"]
                },
                "html": {
                    "type": "custom",
                    "char_filter": ["html_strip"],
                    "tokenizer": "standard",
                    "filter": ["asciifolding", "lowercase", "stop", "snowball"]
                }
            },
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type" : "edgeNGram",
                    "min_gram" : "2",
                    "max_gram" : "20"
                }
            }
        }
    }
}

def create_polymorphic_indexes(sender, **kwargs):
    """This is a post_syncdb (in 1.7, post_migrate) signal that creates indexes and mappings
    for the polymorphic models in this model file."""

    indexes = {}

    for model in get_models(sender):
        if isinstance(model(), PolymorphicIndexable):
            index = model.get_index_name()
            if index not in indexes:
                indexes[index] = {}
            indexes[index][model.get_mapping_type_name()] = model.get_mapping()

    es = get_es(urls=settings.ES_URLS)
    for index, mappings in indexes.items():
        try:
            print("Creating: %s" % index)
            es.create_index(index, settings= {
                "mappings": mappings,
                "settings": ES_SETTINGS
            })
        except IndexAlreadyExistsError:
            for doctype,mapping in mappings.items():
                try:
                    es.put_mapping(index, doctype, mapping)
                except ElasticHttpError as e:
                    print("ES Error: %s" % e.error)
        except ElasticHttpError as e:
            print("ES Error: %s" % e.error)

# Let's register a post_syncdb signal for everything that's PolymorphicIndexable
registered_modules = set()
for name,model in polymorphic_indexable_registry.all_models.items():
    if model.__module__ not in registered_modules:
        post_syncdb.connect(create_polymorphic_indexes, importlib.import_module(model.__module__))
        registered_modules.add(model.__module__)
