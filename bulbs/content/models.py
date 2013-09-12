"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""


from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.backends import util
from django.template.defaultfilters import slugify
from django.utils import timezone

from bulbs.images.fields import RemoteImageField

from elasticutils import SearchResults, S
from elasticutils.contrib.django import get_es
from polymorphic import PolymorphicModel


def deserialize_polymorphic_model(data):
    """Deserializes simple polymorphic models."""
    content_type = ContentType.objects.get_for_id(data['polymorphic_ctype'])
    if content_type:
        klass = content_type.model_class()
        instance = klass.from_source(data)
        return instance


class ContentSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = []
        for result in results:
            obj = deserialize_polymorphic_model(result['_source'])
            self.objects.append(obj)

    def __iter__(self):
        return self.objects.__iter__()


class ContentS(S):

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

    def get_results_class(self):
        """Returns the results class to use

        The results class should be a subclass of SearchResults.

        """
        if self.as_list or self.as_dict:
            return super(ContentS, self).get_results_class()

        return ContentSearchResults


class TagSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = [
            deserialize_polymorphic_model(result['_source']) for result in results
        ]

    def __iter__(self):
        return self.objects.__iter__()


class TagS(S):

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
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(self)
        return serializer.data

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
        return result

    @classmethod
    def from_source(cls, source):
        serializer_class = cls.get_serializer_class()
        serializer = serializer_class(data=source)
        if serializer.is_valid():
            if 'id' in source:
                serializer.object.id = source['id']
                # TODO: arrrrrrgh ugh
                serializer.object.content = source['id']
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

    @classmethod
    def get_serializer_class(cls):
        raise NotImplementedError('%s must define `get_serializer_class`.' % cls.__name__)


class Tag(PolymorphicIndexable, PolymorphicModel):
    """Model for tagging up Content."""
    name = models.CharField(max_length=255)
    slug = models.SlugField()

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
            'name': {'type': 'string', 'index': 'not_analyzed'},
            'slug': {'type': 'string', 'index': 'not_analyzed'},
        })
        return props
    
    @classmethod
    def get_serializer_class(cls):
        from .serializers import TagSerializer
        return TagSerializer

    @classmethod
    def search(cls, **kwargs):
        """Search tags...profit."""
        index = settings.ES_INDEXES.get('default')
        results = TagS().es(urls=settings.ES_URLS).indexes(index)
        name = kwargs.pop('name', '')
        if name:
            results = results.query(name__prefix=name, boost=4, should=True).query(name__fuzzy={
                'value': name,
                'prefix_length': 1,
                'min_similarity': 0.35
            }, should=True)

        types = kwargs.pop('types', [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*[
                type_classname for type_classname in kwargs['types'] \
                if type_classname in cls.get_doctypes()
            ])
        else:
            results = results.doctypes(*cls.get_doctypes().keys())
        return results


class Section(Tag):
    """Tag subclass which represents major sections of the site."""
    class Meta(Tag.Meta):
        proxy = True


class Content(PolymorphicIndexable, PolymorphicModel):
    """The base content model from which all other content derives."""
    published = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=512)
    slug = models.SlugField(blank=True, default='')
    description = models.TextField(max_length=1024, blank=True, default='')
    image = RemoteImageField(null=True, blank=True)
    
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _tags = models.TextField(null=True, blank=True)  # A return-separated list of tag names, exposed as a list of strings
    feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)
    _cache = {}  # This is a cache for the content doctypes

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
            'title': {'type': 'string'},
            'slug': {'type': 'string'},
            'description': {'type': 'string'},
            'image': {'type': 'integer'},
            'feature_type': {
                'type': 'multi_field',
                'fields': {
                    'feature_type': {'type': 'string', 'index': 'not_analyzed'},
                    'slug': {'type': 'string', 'index': 'not_analyzed'}
                }
            },
            'tags': {
                'properties': Tag.get_mapping_properties()
            }
        })
        return properties

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ContentSerializerReadOnly
        return ContentSerializerReadOnly

    @classmethod
    def get_writable_serializer_class(cls):
        from .serializers import ContentSerializer
        return ContentSerializer

    @classmethod
    def search(cls, **kwargs):
        """
        If ElasticSearch is being used, we'll use that for the query, and otherwise
        fall back to Django's .filter().

        Allowed params:

         * query
         * tag(s)
         * type(s)
         * feature_type(s)
         * published
        """
        index = settings.ES_INDEXES.get('default')
        results = ContentS().es(urls=settings.ES_URLS).indexes(index)
        if kwargs.get('pk'):
            try:
                pk = int(kwargs['pk'])
            except ValueError:
                pass
            else:
                results = results.query(id=kwargs['pk'])

        if kwargs.get('query'):
            results = results.query(_all__text_phrase=kwargs.get('query'))

        if kwargs.get('published', True):
            now = timezone.now()
            results = results.query(published__lte=now, must=True)

        for tag in kwargs.get('tags', []):
            tag_query_string = 'tags.slug:%s' % tag
            results = results.query(__query_string=tag_query_string)

        for feature_type in kwargs.get('feature_types', []):
            feature_type_query_string = 'feature_type.slug:%s' % feature_type
            results = results.query(__query_string=feature_type_query_string)

        types = kwargs.pop('types', [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*[
                type_classname for type_classname in types \
                if type_classname in cls.get_doctypes()
            ])
        else:
            results = results.doctypes(*cls.get_doctypes().keys())

        return results.order_by('-published')


def content_tags_changed(sender, instance=None, action='', **kwargs):
    """Reindex content tags when they change."""
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

