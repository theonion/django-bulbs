from django.db.models.signals import post_syncdb
from django.conf import settings
from django.db import models

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

import bulbs.content.models
from bulbs.indexable import PolymorphicIndexable

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

def sync_es(sender, **kwargs):
    # Your specific logic here
    es = get_es(urls=settings.ES_URLS)
    index = settings.ES_INDEXES.get('default')

    mappings = {}
    for name, model in bulbs.content.models.Content.get_doctypes().items():
        mappings[name] = model.get_mapping()

    for name, model in bulbs.content.models.Tag.get_doctypes().items():
        mappings[name] = model.get_mapping()

    try:
        es.create_index(index, settings= {
            "mappings": mappings,
            "settings": ES_SETTINGS
        })
    except IndexAlreadyExistsError:
        pass
    except ElasticHttpError as e:
        print("ES Error: %s" % e.error)


def create_polymorphic_indexes(sender, **kwargs):

    indexes = {}
    mappings = {}

    for app in models.get_apps():
        for model in models.get_models(app, include_auto_created=True):
            if isinstance(model(), PolymorphicIndexable):
                index = model.get_index_name()
                name = model.get_mapping_type_name()
                if model.get_index_name() in indexes:
                    indexes[index][name] = model.get_mapping()
                else:
                    indexes[index]= {
                        name: model.get_mapping()
                    }

    es = get_es(urls=settings.ES_URLS)
    for index,mappings in indexes.items():
        try:
            es.create_index(index, settings= {
                "mappings": mappings,
                "settings": ES_SETTINGS
            })
        except IndexAlreadyExistsError:
            pass
        except ElasticHttpError as e:
            print("ES Error: %s" % e.error)

post_syncdb.connect(create_polymorphic_indexes, sender=bulbs.content.models)
post_syncdb.connect(sync_es, sender=bulbs.content.models)
