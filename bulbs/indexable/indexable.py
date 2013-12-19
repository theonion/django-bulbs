from django.conf import settings
from django.db import models

from elasticutils import S, MappingType, SearchResults
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
        except IndexAlreadyExistsError:
            pass
        except ElasticHttpError as e:
            print("ES Error: %s" % e.error)


class ModelSearchResults(SearchResults):
    """This is a little hackey, but in this class, "type" is a polymorphic classmethod
    that we're supposed to return results for."""

    def set_objects(self, results):
        ids = list(int(r['_id']) for r in results)
        model_objects = self.type.objects.in_bulk(ids)
        self.objects = [
            model_objects[id] for id in ids if id in model_objects
        ]

    def __iter__(self):
        return self.objects.__iter__()


class PolymorphicS(S):
    """A custom S class, adding a few methods to ease searching for Polymorphic objects"""

    def __init__(self, type_=None, klass=None):
        """When it comes to PolymorphicS objects, we always want a PolymorphicModel class,
        instead of the MappingType that elasticutils uses, so we'll pass it in to the init method."""
        super(PolymorphicS, self).__init__(type_=type_)
        self.klass = klass
        self.as_models = False

    def _clone(self, next_step=None):
        """Since we have some special stuff in this S class, we need to pass it along when we clone."""
        new = super(PolymorphicS, self)._clone(next_step=next_step)
        new.klass = self.klass
        new.as_models = self.as_models
        return new

    def instanceof(self, klass, exact=False):
        """This gets results that are of this type, or inherit from it.

        If exact is True, only results for this exact class are returned. Otherwise, child objects
        are included in the response."""

        def _get_doctypes(klass):
            """This is a simple recusive method to build a list of doctypes from the ancestors
            of this class"""
            doctypes = [klass.get_mapping_type_name()]
            for subklass in klass.__subclasses__():
                doctypes.extend(_get_doctypes(subklass))
            return doctypes

        if exact is False:
            doctypes = _get_doctypes(klass)
        else:
            doctypes = [klass.get_mapping_type_name()]

        return self._clone(next_step=('doctypes', doctypes))

    def get_results_class(self):
        if self.as_models:
            return ModelSearchResults
        return super(PolymorphicS, self).get_results_class()

    def _do_search(self):
        """
        Perform the search, then convert that raw format into a
        SearchResults instance and return it.
        """
        if self._results_cache is None:
            response = self.raw()
            ResultsClass = self.get_results_class()
            results = self.to_python(response.get('hits', {}).get('hits', []))

            # This is a little terrible, but the ModelSearchResults expects a "type" that's an actual polymorphicmodel class.s
            if ResultsClass == ModelSearchResults:
                self._results_cache = ResultsClass(self.klass, response, results, self.fields)
            else:
                self._results_cache = ResultsClass(self.type, response, results, self.fields)
        return self._results_cache

    def full(self):
        """This will allow the search to return full model instances, using ModelSearchResults"""
        self.as_models = True
        return self._clone(next_step=('values_list', ['_id']))

class SearchManager(models.Manager):
    """This custom Manager provides some helper methods to easily query and filter elasticsearch
    results for polymorphic objects."""


    def s(self):
        """Returns a PolymorphicS() instance, using an ES URL from the settings, and an index
        from this manager's model"""
        return PolymorphicS(klass=self.model).es(urls=settings.ES_URLS).indexes(self.model.get_index_name())

    @property
    def es(self):
        """Returns a pyelasticsearch object, using the ES URL from the Django settings"""
        return get_es(urls=settings.ES_URLS)

    def refresh(self):
        """Refreshes the index for this object"""
        return self.es.refresh(index=self.model.get_index_name())

    def query(self, **kwargs):
        """Just a simple bridge to elasticutils' S().query(), prepopulating the URL
        and index information"""
        return self.s().query(**kwargs)

    def filter(self, **kwargs):
        """Just a simple bridge to elasticutils' S().filter(), prepopulating the URL
        and index information"""
        return self.s().filter(**kwargs)


class PolymorphicIndexable(object):
    """Base mixin for polymorphic indexin'"""

    search = SearchManager()

    def extract_document(self):
        return {
            'polymorphic_ctype': self.polymorphic_ctype_id,
            self._meta.pk.name : self.pk
        }

    @classmethod
    def get_base_class(cls):
        while cls.__bases__[0] != PolymorphicIndexable:
            cls = cls.__bases__[0]
        return cls

    @classmethod
    def get_index_name(cls):
        return cls.get_base_class()._meta.db_table

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
        """By default, we'll be using the db_table property to get the ES doctype for this object"""
        return cls._meta.db_table

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