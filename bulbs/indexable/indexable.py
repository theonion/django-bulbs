from django.conf import settings
from django.db import models

from elasticutils import S
from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

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
            print("Creating index: %s" % index)
        except IndexAlreadyExistsError:
            pass
        except ElasticHttpError as e:
            print("ES Error: %s" % e.error)


class SearchManager(models.Manager):
    
    def es(self):
        return S().es(urls=settings.ES_URLS).indexes(self.model.get_index_name())

    def query(self, **kwargs):
        return self.es().query(**kwargs)

    def filter(self, **kwargs):
        return self.es().filter(**kwargs)


class PolymorphicIndexable(object):
    """Base mixin for polymorphic indexin'"""

    search = SearchManager()

    def extract_document(self):
        return {
            'polymorphic_ctype': self.polymorphic_ctype_id,
            self._meta.pk.name : self.pk
        }

    @classmethod
    def get_index_name(cls):
        while cls.__bases__[0] != PolymorphicIndexable:
            cls = cls.__bases__[0]
        return '%s_%s' % (cls._meta.app_label, cls.__name__.lower())

    @classmethod
    def get_es(self):
        return get_es(urls=settings.ES_URLS).index(self.get_index_name())

    @classmethod
    def get_mapping(cls):
        return {
            cls.get_mapping_type_name(): {
                '_id': {
                    'path': cls._meta.pk.name
                },
                'properties': cls.get_mapping_properties()
            }
        }

    @classmethod
    def get_mapping_properties(cls):
        return {
            cls._meta.pk.name : {'type': 'integer'},
            'polymorphic_ctype': {'type': 'integer'}
        }

    @classmethod
    def get_mapping_type_name(cls):
        return '%s_%s' % (cls._meta.app_label, cls.__name__.lower())

    def index(self, refresh=False):
        es = get_es(urls=settings.ES_URLS)
        doc = self.extract_document()
        # NOTE: this could be made more efficient with the `doc_as_upsert`
        # param when the following pull request is merged into pyelasticsearch:
        # https://github.com/rhec/pyelasticsearch/pull/132
        es.update(
            self.get_index_name(),
            self.get_mapping_type_name(),
            self.id,
            doc=doc,
            upsert=doc
        )

    def save(self, index=True, refresh=False, *args, **kwargs):
        result = super(PolymorphicIndexable, self).save(*args, **kwargs)
        if index:
            self.index(refresh=refresh)
        self._index = index
        return result