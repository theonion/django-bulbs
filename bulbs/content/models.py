"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""


from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.backends import util
from django.template.defaultfilters import slugify
from django.utils import timezone

from bulbs.images.fields import RemoteImageField

from elasticutils import SearchResults, S
from elasticutils.contrib.django import get_es
from polymorphic import PolymorphicModel, PolymorphicManager


def fetch_cached_models_by_id(model_class, model_ids, key_template='bulkcache/%s/id/%d'):
    """Bulk loads models by first checking the cache, then db."""
    result_map = {}
    cache_keys = {
        model_id: key_template % (model_class._meta.db_table, model_id)
        for model_id in model_ids
    }
    # get all of the desired objects which are already cached
    cached_results = cache.get_many(cache_keys.values())
    for key, obj in cached_results.items():
        result_map[obj.id] = obj
        del cache_keys[obj.id]
    # load up the remaining, uncached objects from the db and cache them:
    if cache_keys:
        db_results = model_class.objects.in_bulk(cache_keys.keys())
        for id, obj in db_results.items():
            result_map[id] = obj
        cache.set_many({
            cache_keys[id]: obj for id, obj in db_results.items()
        })
    # return a correctly ordered list of the objects
    return [result_map[id] for id in model_ids]


def deserialize_polymorphic_model(data):
    """Deserializes simple polymorphic models."""
    content_type = ContentType.objects.get_for_id(data['polymorphic_ctype'])
    if content_type:
        klass = content_type.model_class()
        instance = klass.from_source(data)
        return instance


class PatchedS(S):
    """Common patches for the S model."""
    def all(self):
        """
        Fixes the default `S.all` method given by elasticutils.
        `S` generally looks like django queryset but differs in
        a few ways, one of which is `all`. Django `QuerySet` just
        returns a clone for `all` but `S` wants to return all
        the documents. This makes `all` at least respect slices
        but the real fix is to probably make `S` work more like
        `QuerySet`.
        """
        if self.start == 0 and self.stop is None:
            # no slicing has occurred. let's get all of the records.
            count = self.count()
            return self[:count].execute()
        return self.execute()

    def model_facet_counts(self, model_class):
        """Retrieves facet counts and interpretes the faceted field as
        the pk of the `model_class` argument. The models are then fetched and
        annotated with `facet_count`.

        Requires that a valid facet query has already been added to
        this S object.
        """
        id_facet_counts = self.facet_counts().get('id', None)
        if id_facet_counts is None:
            raise ValueError('No id facets found.')
        # the facet "term" is the id. let's get a list of those.
        ids = [fc['term'] for fc in id_facet_counts]
        # NOTE: The Tag model is hard-coded in here right now.
        models = fetch_cached_models_by_id(model_class, ids)
        # annotate models with facet counts
        for model, facet_result in zip(models, id_facet_counts):
            model.facet_count = facet_result['count']
        return models


class ModelSearchResults(SearchResults):
    """Takes the 'id' list returned by a ModelS and delivers model instances."""
    @classmethod
    def get_model(cls):
        raise NotImplementedError('ModelSearchResults requires a `get_model` method.')
        
    def set_objects(self, results):
        ids = list(int(r['_id']) for r in results)
        model_objects = self.get_model().objects.in_bulk(ids)
        self.objects = [
            model_objects[id] for id in ids if id in model_objects
        ]

    def __iter__(self):
        return self.objects.__iter__()


class ModelS(PatchedS):
    """ModelS makes queries which return ids from ES and result in models."""
    results_class = ModelSearchResults

    def __init__(self, *args, **kwargs):
        super(ModelS, self).__init__(*args, **kwargs)
        self.steps.append(('values_list', ['_id']))

    def get_results_class(self):
        """Returns the results class to use.

        The results class should be a subclass of SearchResults.
        """
        return self.results_class


class ContentSearchResults(ModelSearchResults):
    @classmethod
    def get_model(cls):
        return Content


class ContentS(ModelS):
    results_class = ContentSearchResults


class TagSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = [
            deserialize_polymorphic_model(result['_source']) for result in results
        ]

    def __iter__(self):
        return self.objects.__iter__()


class TagS(PatchedS):

    def get_results_class(self):
        """Returns the results class to use

        The results class should be a subclass of SearchResults.

        """
        if self.as_list or self.as_dict:
            return super(TagS, self).get_results_class()

        return TagSearchResults


class PolymorphicIndexable(object):
    """Base mixin for polymorphic indexin'"""
    def extract_document(self):
        return {
            'polymorphic_ctype': self.polymorphic_ctype_id,
            'id': self.pk
        }

    def index(self, refresh=False):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        es.index(
            index,
            self.get_mapping_type_name(),
            self.extract_document(),
            self.id,
            refresh=refresh
        )

    def save(self, index=True, refresh=False, *args, **kwargs):
        result = super(PolymorphicIndexable, self).save(*args, **kwargs)
        if index:
            self.index(refresh=refresh)
        self._index = index
        return result

    @classmethod
    def from_source(cls, source):
        serializer_class = cls.get_serializer_class()
        serializer = serializer_class(data=source)
        if serializer.is_valid():
            serializer.object.pk = source[cls.polymorphic_primary_key_name] 
            return serializer.object
        else:
            raise RuntimeError(serializer.errors)

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


class TagManager(PolymorphicManager):
    def search(self, s_class=TagS, **kwargs):
        """Search tags...profit."""
        index = settings.ES_INDEXES.get('default')
        results = s_class().es(urls=settings.ES_URLS).indexes(index)
        name = kwargs.pop('name', '')
        if name:
            results = results.query(name__fuzzy={
                'value': name,
                'prefix_length': 1,
                'min_similarity': 0.35
            }, should=True)

        types = kwargs.pop('types', [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*[
                type_classname for type_classname in kwargs['types'] \
                if type_classname in self.model.get_doctypes()
            ])
        else:
            results = results.doctypes(*self.model.get_doctypes().keys())
        return results

class Tag(PolymorphicIndexable, PolymorphicModel):
    """Model for tagging up Content."""
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    objects = TagManager()

    _doctype_cache = {}

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    @classmethod
    def get_doctypes(cls):
        if len(cls._doctype_cache) == 0:
            for app in models.get_apps():
                for model in models.get_models(app, include_auto_created=True):
                    if isinstance(model(), Tag):
                        cls._doctype_cache[model.get_mapping_type_name()] = model
        return cls._doctype_cache

    @classmethod
    def get_mapping_properties(cls):
        props = super(Tag, cls).get_mapping_properties()
        props.update({
            'name': {
                'type': 'multi_field',
                'fields': {
                    'name': {
                        'type': 'string',
                        'analyzer': 'standard'
                    },
                    'slug': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    }
                }
            },
            'slug': {'type': 'string', 'index': 'not_analyzed'},
        })
        return props
    
    def extract_document(self):
        data = super(Tag, self).extract_document()
        data.update({
            'name': self.name,
            'slug': self.slug
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        from .serializers import TagSerializer
        return TagSerializer


class ContentManager(PolymorphicManager):
    def search(self, s_class=ContentS, **kwargs):
        """
        Queries using ElasticSearch, returning an elasticutils queryset.

        Allowed params:

         * query
         * tags
         * types
         * feature_types
         * published
        """
        
        index = settings.ES_INDEXES.get('default')
        results = s_class().es(urls=settings.ES_URLS).indexes(index)
        if kwargs.get('pk'):
            try:
                pk = int(kwargs['pk'])
            except ValueError:
                pass
            else:
                results = results.query(id=pk)

        if 'pk' in kwargs:
            return self.filter(pk=kwargs.get('pk'))

        if 'query' in kwargs:
            results = results.query(_all__text_phrase=kwargs.get('query'))

        if kwargs.get('published', True):
            now = timezone.now()
            results = results.query(published__lte=now, must=True)

        if 'tags' in kwargs:
            tags = kwargs['tags']
            results = results.filter(**{'tags.slug__in':tags})

        if 'feature_types' in kwargs:
            feature_types = kwargs['feature_types']
            results = results.filter(**{'feature_type.slug__in':feature_types})

        if 'authors' in kwargs:
            authors = kwargs['authors']
            results = results.filter(**{'authors.username__in':authors})

        types = kwargs.pop('types', [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*[
                type_classname for type_classname in types \
                if type_classname in self.model.get_doctypes()
            ])
        else:
            results = results.doctypes(*self.model.get_doctypes().keys())

        return results.order_by('-published')


class Content(PolymorphicIndexable, PolymorphicModel):
    """The base content model from which all other content derives."""
    published = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=512)
    slug = models.SlugField(blank=True, default='')
    description = models.TextField(max_length=1024, blank=True, default='')
    image = RemoteImageField(null=True, blank=True)
    
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)
    _cache = {}  # This is a cache for the content doctypes

    objects = ContentManager()

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        return reverse('content-detail-view', kwargs=dict(pk=self.pk, slug=self.slug))

    @property
    def byline(self):
        # If we have authors, just put them in a list
        if self.authors.exists():
            return ', '.join([user.get_full_name() for user in self.authors.all()])

        # Well, shit. I guess there's no byline.
        return None

    def build_slug(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.build_slug())[:self._meta.get_field('slug').max_length]

        return super(Content, self).save(*args, **kwargs)

    # class methods ##############################

    @classmethod
    def get_doctypes(cls):
        if len(cls._cache) == 0:
            for app in models.get_apps():
                for model in models.get_models(app, include_auto_created=True):
                    if isinstance(model(), Content):
                        cls._cache[model.get_mapping_type_name()] = model
        return cls._cache

    @classmethod
    def get_mapping_properties(cls):
        properties = super(Content, cls).get_mapping_properties()
        properties.update({
            'published': {'type': 'date'},
            'title': {'type': 'string', 'analyzer': 'snowball'},
            'slug': {'type': 'string'},
            'description': {'type': 'string'},
            'image': {'type': 'string'},
            'feature_type': {
                'type': 'multi_field',
                'fields': {
                    'feature_type': {'type': 'string', 'analyzer': 'standard'},
                    'slug': {'type': 'string', 'index': 'not_analyzed'}
                }
            },
            'authors': {
                'properties': {
                    'first_name': {'type': 'string'},
                    'id': {'type': 'long'},
                    'last_name': {'type': 'string'},
                    'username': {'type': 'string', 'index': 'not_analyzed'}
                }
            },
            'tags': {
                'properties': Tag.get_mapping_properties()
            }
        })
        return properties

    def extract_document(self):
        data = super(Content, self).extract_document()
        data.update({
            'published'        : self.published,
            'title'            : self.title,
            'slug'             : self.slug,
            'description'      : self.description,
            'image'            : self.image.name if self.image else None,
            'feature_type'     : self.feature_type,
            'feature_type.slug': slugify(self.feature_type),
            'authors': [{
                'first_name': author.first_name,
                'id'        : author.id,
                'last_name' : author.last_name,
                'username'  : author.username
            } for author in self.authors.all()],
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            } for tag in self.tags.all()]
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ContentSerializerReadOnly
        return ContentSerializerReadOnly

    @classmethod
    def get_writable_serializer_class(cls):
        from .serializers import ContentSerializer
        return ContentSerializer


def content_tags_changed(sender, instance=None, action='', **kwargs):
    """Reindex content tags when they change."""
    if getattr(instance, "_index", True):  # TODO: Rethink this hackey shit. Is there a better way?
        es = get_es()
        indexes = settings.ES_INDEXES
        index = indexes['default']
        doc = {}
        doc['tags'] = [tag.extract_document() for tag in instance.tags.all()]
        es.update(index, instance.get_mapping_type_name(), instance.id, doc=doc, refresh=True)


models.signals.m2m_changed.connect(
    content_tags_changed,
    sender=Content.tags.through,
    dispatch_uid='content_tags_changed_signal'
)

