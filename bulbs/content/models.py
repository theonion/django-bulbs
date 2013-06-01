from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.db.backends import util

from elasticutils import get_es, S, SearchResults
from pyelasticsearch.exceptions import ElasticHttpNotFoundError, InvalidJsonResponseError

from bulbs.images.models import Image
from bulbs.content.base62 import base10to62, base62to10


# This function is needed because data descriptors must be defined on a class
# object, not an instance, to have any effect.

def readonly_content_factory(model):
    """
    Returns a class object that is a copy of "model" with the specified "attrs"
    being replaced with DeferredAttribute objects. The "pk_value" ties the
    deferred attributes to a particular instance of the model.
    """
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    # The app_cache wants a unique name for each model, otherwise the new class
    # won't be created (we get an old one back). Therefore, we generate the
    # name using the passed in attrs. It's OK to reuse an existing class
    # object if the attrs are identical.
    name = "%s_Readonly" % model.__name__
    name = util.truncate_name(name, 80, 32)

    overrides = {
        "Meta": Meta,
        "__module__": model.__module__,
        "_readonly": True,
    }
    # TODO: Add additional deferred fields here, just as placeholders.
    return type(str(name), (model,), overrides)


class ContentishSearchResults(SearchResults):
    def set_objects(self, results):
        self.objects = []
        for result in results:
            cls = Contentish.get_doctypes().get(result['_type'])
            if cls:
                readonly_cls = readonly_content_factory(cls)
                pk = result['_source'].get('object_id')
                obj = readonly_cls(pk=pk)
                obj.load_from_source(result['_source'])
                self.objects.append(obj)

    def __iter__(self):
        return self.objects.__iter__()


class ContentishS(S):

    def get_results_class(self):
        """Returns the results class to use

        The results class should be a subclass of SearchResults.

        """
        if self.as_list or self.as_dict:
            return super(ContentishS, self).get_results_class()

        return ContentishSearchResults


class TagishSearchResults(SearchResults):
    def set_objects(self, results):
        # TODO: Handle DB backed tags
        self.objects = [
            Tagish(slug=result['_source']['slug'], name=result['_source']['name'])
            for result in results]

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
        return "Tag: %s" % self.name

    def save(self, *args, **kwargs):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')

        # The default slug for a tagish object is "[slugified name]-[slugified classname]"
        # If that's already taken, we start appending numbers
        counter = 1
        slug = slugify("%s %s" % (self.name, self.__class__.__name__))
        while self.slug is None or self.slug == '':
            try:
                es_tag = es.get(index, 'tag', slug)
            except ElasticHttpNotFoundError:
                self.slug = slug
                break

            slug = slugify("%s %s %s" % (self.name, self.__class__.__name__, counter))
            counter += 1

        super(Tagish, self).save(*args, **kwargs)
        self.index()


    @classmethod
    def get(cls, slug):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        try:
            es_tag = es.get(index, 'tag', slug)
        except ElasticHttpNotFoundError:
            raise cls.ObjectDoesNotExist

        obj = cls(
            name=es_tag['_source']['name'],
            slug=es_tag['_source']['slug']
        )
        return obj

    @classmethod
    def from_name(cls, name):
        obj = cls()
        obj.name = name
        obj.slug = slugify(name)
        return obj

    def index(self):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
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
        return Contentish.search(tags=[self.slug])

BASE_CONTENT_MAPPING = {
    "properties": {
        "object_id": {"type": "integer"},
        "title": {"type": "string"},
        "slug": {"type": "string", "index": "not_analyzed"},
        "subhead": {"type": "string"},
        "description": {"type": "string"},
        "feature_type": {
            "type": "multi_field",
            "fields": {
                "feature_type": {"type": "string", "index": "analyzed"},
                "slug": {"type": "string", "index": "not_analyzed"}
            }
        },
        "image": {"type": "integer"},
        "byline": {"type": "string"},
        "published": {"type": "date"},
        "tags": {
            "properties": {
                "name": {"type": "string"},
                "slug": {"type": "string", "index": "not_analyzed"}
            }
        }
    }
}


class Contentish(models.Model):
    """
    Abstract base class for objects that'd like to be considered 'content.'
    """

    elastic_id = models.SlugField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.CharField(max_length=1024)
    image = models.ForeignKey(Image, null=True, blank=True)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)  # This is an overridable field that is by default the author names
    _tags = models.TextField(null=True, blank=True)  # A return-separated list of tag names, exposed as a list of strings
    _feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)
    _cache = {}  # This is a cache for the content doctypes

    class Meta:
        abstract = True

    def __unicode__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        return ""

    def save(self, *args, **kwargs):
        super(Contentish, self).save(*args, **kwargs)
        if self.elastic_id is None:
            elastic_id = "%d%d" % (ContentType.objects.get_for_model(self).id, self.id)
            self.elastic_id = base10to62(int(elastic_id))
            super(Contentish, self).save(update_fields=['elastic_id'])
        self.index()

    @classmethod
    def get_doctypes(cls):
        if len(cls._cache) == 0:
            for app in models.get_apps():
                for model in models.get_models(app, include_auto_created=True):
                    if isinstance(model(), Contentish):
                        cls._cache[model.get_mapping_type_name()] = model
        return cls._cache

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

        results = ContentishS().es(urls=settings.ES_URLS).indexes(index)
        if kwargs.get('published', True):
            now = timezone.now()
            results = results.query(published__lte=now, must=True)

        for tag in kwargs.get('tags', []):
            tag_query_string = "tags.slug:%s" % tag
            results = results.query(__query_string=tag_query_string)

        for feature_type in kwargs.get('feature_types', []):
            feature_type_query_string = "feature_type.slug:%s" % feature_type
            results = results.query(__query_string=feature_type_query_string)

        if 'types' in kwargs:
            results = results.doctypes(*[type_class.get_mapping_type_name() for type_class in kwargs['types']])
        else:
            results = results.doctypes(*cls.get_doctypes().keys())

        return results.order_by('-published')

    @property
    def tags(self):
        if self._tags:
            return Tagish.search().query(slug__terms=[slugify(tag) for tag in self._tags.split("\n")])
        return []

    @tags.setter
    def tags(self, value):
        if self._readonly:
            raise AttributeError("This content object is read only.")
        # TODO: is this too terrible? Should a setter really have this behavior? Too implicit?
        if isinstance(value, basestring):
            self._tags = "\n".join([tag.strip() for tag in self._tags.split("\n")])
        else:
            self._tags = "\n".join([tag.strip() for tag in value])

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
            return ", ".join([user.get_full_name() for user in self.authors.all()])

        # Well, shit. I guess there's no byline.
        return None

    @byline.setter
    def byline(self, value):
        if self._readonly:
            raise AttributeError("This content object is read only.")
        self._byline = value

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
            raise AttributeError("This content object is read only.")
        self._feature_type = value

    # ElasticUtils stuff
    def index(self):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        es.index(index, self.get_mapping_type_name(), self.extract_document(), self.elastic_id)

        if not self._tags:
            return

        for tag_name in self._tags.split("\n"):
            tag = Tagish.from_name(tag_name)
            try:
                tag = es.get(index, 'tag', tag.slug)
            except ElasticHttpNotFoundError:
                tag.index()

    def load_from_source(self, _source):
        self.slug = _source['slug']
        self.title = _source['title']
        self.description = _source['description']
        self.subhead = _source['subhead']
        self.published = _source['published']
        self._feature_type = _source['feature_type']
        self._tags = "\n".join([tag['name'] for tag in _source['tags']])

    @classmethod
    def get_mapping_type_name(cls):
        return "%s_%s" % (cls._meta.app_label, cls.__name__.lower())

    @classmethod
    def get_mapping(cls):
        return {
            cls.get_mapping_type_name(): BASE_CONTENT_MAPPING
        }

    def extract_document(self):
        data = {
            'object_id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'image': self.image_id,
            'byline': self.byline,
            'subhead': self.subhead,
            'published': self.published,
            'feature_type': self.feature_type,
            'feature_type.slug': slugify(self.feature_type)
        }
        if self._tags:
            data['tags'] = [{
                'name': tag_name,
                'slug': slugify(tag_name)
            } for tag_name in self._tags.split("\n")]
        return data
