from collections import Iterable

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.db.backends import util
from django.db.models.query_utils import deferred_class_factory

from elasticutils import SearchResults, S
from elasticutils.contrib.django import get_es
from polymorphic import PolymorphicModel
from pyelasticsearch.exceptions import ElasticHttpNotFoundError, InvalidJsonResponseError

from bulbs.images.models import Image


def readonly_content_factory(model):
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    name = '%s_Readonly' % model.__name__
    name = util.truncate_name(name, 80, 32)

    overrides = {
        'Meta': Meta,
        '__module__': model.__module__,
        '_readonly': True,
    }
    # TODO: Add additional deferred fields here, just as placeholders.
    return type(str(name), (model,), overrides)


class ContentSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = []
        for result in results:
            cls = Content.get_doctypes().get(result['_type'])
            if cls:
                readonly_cls = readonly_content_factory(cls)
                obj = readonly_cls.from_source(result['_source'])
                self.objects.append(obj)

    def __iter__(self):
        return self.objects.__iter__()


class ContentS(S):

    def get_results_class(self):
        """Returns the results class to use

        The results class should be a subclass of SearchResults.

        """
        if self.as_list or self.as_dict:
            return super(ContentS, self).get_results_class()

        return ContentSearchResults


class TagishSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = [Tagish.from_source(result['_source']) for result in results]

    def __iter__(self):
        return self.objects.__iter__()


class TagishS(S):

    def get_results_class(self):
        """Returns the results class to use

        The results class should be a subclass of SearchResults.

        """
        if self.as_list or self.as_dict:
            return super(TagishS, self).get_results_class()

        return TagishSearchResults


class Tagish(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.__class__ == Tagish:
            return 'Tag: %s' % self.name
        else:
            return '%s: %s' % (self.__class__.__name__, self.name)

    def save(self, *args, **kwargs):
        es = get_es()
        indexes = settings.ES_INDEXES
        index = indexes.get('tag') or indexes['default']

        # The default slug for a tagish object is "[slugified name]-[slugified classname]"
        # If that's already taken, we start appending numbers
        counter = 1
        slug = slugify('%s %s' % (self.name, self.__class__.__name__))
        while self.slug is None or self.slug == '':
            try:
                es_tag = es.get(index, 'tag', slug)
            except ElasticHttpNotFoundError:
                self.slug = slug
                break

            slug = slugify('%s %s %s' % (self.name, self.__class__.__name__, counter))
            counter += 1

        super(Tagish, self).save(*args, **kwargs)
        self.index()

    @classmethod
    def get(cls, slug):
        es = get_es()
        indexes = settings.ES_INDEXES
        index = indexes.get('tag') or indexes['default']
        try:
            es_tag = es.get(index, 'tag', slug)
        except ElasticHttpNotFoundError:
            raise cls.ObjectDoesNotExist

        return cls.from_source(es_tag['_source'])

    @classmethod
    def from_source(cls, _source):
        if _source.get('object_id'):
            model = ContentType.objects.get_for_id(_source['content_type']).model_class()
            # Get the attributes to be deferred.
            attrs = [fn for fn in model._meta.get_all_field_names() if fn not in ['pk', 'slug', 'name']]
            model = deferred_class_factory(model, attrs)
            return model(id=_source['object_id'], name=_source['name'], slug=_source['slug'])
        return Tagish(name=_source['name'], slug=_source['slug'])

    @classmethod
    def from_name(cls, name):
        obj = cls()
        obj.name = name
        obj.slug = slugify(name)
        return obj

    def index(self):
        es = get_es()
        indexes = settings.ES_INDEXES
        index = indexes.get('tag') or indexes['default']
        try:
            response = es.index(index, 'tag', self.extract_document(), self.slug)
        except InvalidJsonResponseError as e:
            print(e.response.content)

    def extract_document(self):
        data = {'name': self.name, 'slug': self.slug}
        if getattr(self, 'id', None):
            data['content_type'] = ContentType.objects.get_for_model(self).id
            data['object_id'] = self.id
        return data

    @classmethod
    def search(cls, query=None):
        index = settings.ES_INDEXES.get('default')
        results = TagishS().es(urls=settings.ES_URLS).indexes(index).doctypes('tag')
        if query:
            results = results.query(name__match={'query': query, 'fuzziness': 0.35})
        return results

    def content(self):
        return Content.search(tags=[self.slug])


class TagishRelatedManage():
    """ This is pretty messy, but it does work. This is basically a related manager-ish
        class that allows adding, removing and retriving the tags from a Content object.
    """

    def __init__(self, content):
        self.content = content

    def _save_tags(self, refresh=False):
        self.content.save(index=False, update_fields=['_tags'])
        es = get_es()
        indexes = settings.ES_INDEXES
        index = indexes.get('tag') or indexes['default']
        doc = {}
        doc['tags'] = [
            {
                'name': tag_name,
                'slug': slugify(tag_name)
            } for tag_name in self.content._tags.split('\n')]
        es.update(index, self.content.get_mapping_type_name(), self.content.elastic_id, doc=doc, refresh=refresh)
        for tag_name in self.content._tags.split('\n'):
            tag = Tagish.from_name(tag_name)
            try:
                tag = es.get(index, 'tag', tag.slug)
            except ElasticHttpNotFoundError:
                tag.index()

    def all(self):
        if self.content._tags:
            return Tagish.search().query(slug__terms=[slugify(tag) for tag in self.content._tags.split('\n')])
        return []

    def remove(self, tags):
        if not isinstance(tags, Iterable):
            tags = [tags]
        if self.content._tags is None:
            tag_list = []
        else:
            tag_list = self.content._tags.split('\n')
        for tag in tags:
            if isinstance(tag, Tagish):
                tag_name = tag.name
            elif isinstance(tag, basestring):
                tag_name = tag
            else:
                raise TypeError('Tags must be strings or Tagish objects')
            if tag_name in tag_list:
                tag_list.remove(tag_name)
            else:
                raise AttributeError('There is no attached tag with the name \"%s\"' % tag_name)
        self.content._tags = '\n'.join(tag_list)
        self._save_tags()

    def add(self, tags):
        if not isinstance(tags, Iterable):
            tags = [tags]
        if self.content._tags is None:
            tag_list = []
        else:
            tag_list = self.content._tags.split('\n')
        for tag in tags:
            if isinstance(tag, Tagish):
                tag_name = tag.name
            elif isinstance(tag, basestring):
                tag_name = tag
            else:
                raise TypeError('Tags must be strings or Tagish objects')
            if tag_name in tag_list:
                raise AttributeError('There is already an attached tag with the name \"%s\"' % tag_name)
            else:
                tag_list
                tag_list.append(tag_name)
        self.content._tags = '\n'.join(tag_list)
        self._save_tags()


class Content(PolymorphicModel):
    """The base content model from which all other content derives."""
    published = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=512)
    slug = models.SlugField()
    description = models.TextField(max_length=1024)
    image = models.ForeignKey(Image, null=True, blank=True)
    
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)  # This is an overridable field that is by default the author names
    _tags = models.TextField(null=True, blank=True)  # A return-separated list of tag names, exposed as a list of strings
    _feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)
    _cache = {}  # This is a cache for the content doctypes

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        return '/content/%d/' % self.id

    def save(self, *args, **kwargs):
        result = super(Content, self).save(*args, **kwargs)
        self.index()
        return result

    @property
    def byline(self):
        # If the subclass has customized the byline accessing, use that.
        if hasattr(self, 'get_byline'):
            return self.get_byline()

        # If we have an override byline, we'll use that first.
        if self._byline:
            return self._byline

        # If we have authors, just put them in a list
        if self.authors.exists():
            return ', '.join([user.get_full_name() for user in self.authors.all()])

        # Well, shit. I guess there's no byline.
        return None

    def extract_document(self):
        doc = {
            'id': self.id,
            'published': self.published,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'image': self.image_id,
            'byline': self.byline,
            'subhead': self.subhead,
            'feature_type': self.feature_type,
            'feature_type.slug': slugify(self.feature_type)
        }
        if self._tags:
            data['tags'] = [{
                'name': tag_name,
                'slug': slugify(tag_name)
            } for tag_name in self._tags.split('\n')]
        return doc


    @property
    def feature_type(self):
        # If the subclass has customized the feature_type accessing, use that.
        if hasattr(self, 'get_feature_type'):
            return self.get_feature_type()

        if self._feature_type:
            return self._feature_type

        return None

    @feature_type.setter
    def feature_type(self, value):
        if self._readonly:
            raise AttributeError('This content object is read only.')
        self._feature_type = value

    # ElasticUtils stuff
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

        if not self._tags:
            return

        for tag_name in self._tags.split('\n'):
            tag = Tagish.from_name(tag_name)
            try:
                tag = es.get(index, 'tag', tag.slug, refresh=refresh)
            except ElasticHttpNotFoundError:
                tag.index()

    @property
    def tags(self):
        if not hasattr(self, '_tag_relation'):
            self._tag_relation = TagishRelatedManage(self)
        return self._tag_relation
        return []

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
    def from_source(cls, _source):
        return cls(
            id=_source['object_id'],
            published=_source['published'],
            title=_source['title'],
            slug=_source['slug'],
            description=_source['description'],
            subhead=_source['subhead'],
            _feature_type=_source['feature_type'],
            _tags='\n'.join([tag['name'] for tag in _source.get('tags', [])])
        )

    @classmethod
    def get_mapping(cls):
        return {
            'properties': {
                'id': {'type': 'integer'},
                'published': {'type': 'date'},
                'title': {'type': 'string'},
                'slug': {'type': 'string'},
                'description': {'type': 'string'},
                'image': {'type': 'integer'},
                'byline': {'type': 'string'},
                'feature_type': {
                    'type': 'multi_field',
                    'fields': {
                        'feature_type': {'type': 'string', 'index': 'analyzed'},
                        'slug': {'type': 'string', 'index': 'not_analyzed'}
                    }
                },
                'tags': {
                    'type': 'multi_field',
                    'properties': {
                        'name': {'type': 'string'},
                        'slug': {'type': 'string', 'index': 'not_analyzed'}
                    }
                }
            }
        }

    @classmethod
    def get_mapping_type_name(cls):
        return '%s_%s' % (cls._meta.app_label, cls.__name__.lower())

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
        results = S().es(urls=settings.ES_URLS).indexes(index)
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

        if 'types' in kwargs:
            results = results.doctypes(*[type_class.get_mapping_type_name() for type_class in kwargs['types']])
        else:
            results = results.doctypes(*cls.get_doctypes().keys())

        return results.order_by('-published')

