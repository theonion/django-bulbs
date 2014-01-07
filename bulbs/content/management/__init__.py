from collections import defaultdict

from django.db.models.signals import post_syncdb
from django.conf import settings

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

import bulbs.content.models

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
    es = get_es(urls=settings.ES_URLS)

    index_mappings = defaultdict(dict)
    for klass in (bulbs.content.models.Content, bulbs.content.models.Tag):
        for index, mappings in bulbs.content.models.Content.get_index_mappings():
            index_mappings[index].update(mappings)
    
    for index, mappings in index_mappings:
        try:
            es.create_index(index, settings={
                "mappings": mappings,
                "settings": ES_SETTINGS
            })
        except IndexAlreadyExistsError:
            for mapping_name, mapping in mappings:
                try:
                    es.put_mapping(index, mapping_name, mapping)
                except ElasticHttpError as e:
                    print("ES Error: %s" % e.error)
                    # MergeExceptionError and want to override conflicts?
                    # es.put_mapping(index, doc_type, mapping, ignore_conflicts=True)
        except ElasticHttpError as e:
            print("ES Error: %s" % e.error)


#post_syncdb.connect(sync_es, sender=bulbs.content.models)
