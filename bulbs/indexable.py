from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from elasticutils.contrib.django import get_es

class PolymorphicIndexable(object):
    """Base mixin for polymorphic indexin'"""
    def extract_document(self):
        return {
            'polymorphic_ctype': self.polymorphic_ctype_id,
            'id': self.pk
        }

    @classmethod
    def get_index_name(cls):
        while cls.__bases__[0] != PolymorphicIndexable:
            cls = cls.__bases__[0]
        return '%s_%s' % (cls._meta.app_label, cls.__name__.lower())

    @classmethod
    def get_es(self):
        return get_es(urls=settings.ES_URLS).index(self.get_index_name())

    def index(self, refresh=False):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        doc = self.extract_document()
        # NOTE: this could be made more efficient with the `doc_as_upsert`
        # param when the following pull request is merged into pyelasticsearch:
        # https://github.com/rhec/pyelasticsearch/pull/132
        es.update(
            index,
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

    @classmethod
    def get_mapping(cls):
        return {
            cls.get_mapping_type_name(): {
                '_id': {
                    'path': 'id'
                },
                'properties': cls.get_mapping_properties()
            }
        }

    @classmethod
    def get_mapping_properties(cls):
        return {
            'id': {'type': 'integer'},
            'polymorphic_ctype': {'type': 'integer'}
        }

    @classmethod
    def get_mapping_type_name(cls):
        return '%s_%s' % (cls._meta.app_label, cls.__name__.lower())