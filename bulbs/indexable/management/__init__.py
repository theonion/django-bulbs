"""This module allows us to automatically"""

import importlib

from django.db import models
from django.conf import settings
from django.db.models.signals import post_syncdb
from django.db.models.loading import get_models

from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from bulbs.indexable import PolymorphicIndexable

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

    for model in get_models(sender.__package__):
        if isinstance(model(), PolymorphicIndexable):
            index = sender.get_index_name()
            if index not in indexes:
                indexes[index] = {}
            indexes[index][model.get_mapping_type_name()] = model.get_mapping()

    es = get_es(urls=settings.ES_URLS)
    for index,mappings in indexes.items():
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


for app in models.get_apps():
    for model in models.get_models(app):
        if isinstance(model(), PolymorphicIndexable):
            post_syncdb.connect(create_polymorphic_indexes, importlib.import_module(model.__module__))

