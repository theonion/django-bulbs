from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType

from elasticutils import get_es, S, MappingType
from pyelasticsearch.exceptions import ElasticHttpNotFoundError

from bulbs.images.models import Image
from bulbs.base.base62 import base10to62, base62to10


class ContentMappingType(MappingType):

    @classmethod
    def get_index(cls):
        index = settings.ES_INDEXES.get('default')
        return index

    @classmethod
    def get_mapping_type_name(cls):
        return 'content'


class ContentishS(S):

    def _do_search(self):
        results = super(ContentishS, self)._do_search()
        objects = []
        for result in results:
            app_label, model = result._type.split("_")
            content_type = ContentType.objects.get_by_natural_key(app_label, model)
            cls = content_type.model_class()
            pk = str(result._id).replace(str(content_type.id), '', 1)
            obj = cls(pk=pk)
            obj.load_from_source(result._source)
            objects.append(obj)
        return objects


class TagishS(S):

    def _do_search(self):
        results = super(TagishS, self)._do_search()
        objects = []
        for result in results:
            obj = Tagish(slug=result._source['slug'], name=result._source['name'])
            objects.append(obj)
        return objects


class Tagish(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        abstract = True

    def __unicode__(self):
        return "Tag: %s" % self.name

    @classmethod
    def from_name(cls, name):
        obj = cls()
        obj.name = name
        obj.slug = slugify(name)
        return obj

    def index(self):
        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        es.index(index, 'tag', self.extract_document(), self.slug)

    def extract_document(self):
        data = {'name': self.name, 'slug': self.slug}
        # if getattr(self, 'id', None):
        #     data['content_type'] = self._meta.db_table
        #     data['object_id'] = self.id
        return data

    @classmethod
    def search(cls, query=None):
        index = settings.ES_INDEXES.get('default')
        results = TagishS().es(urls=settings.ES_URLS).indexes(index).doctypes('tag')
        if query:
            results = results.query(name__wildcard="%s*" % query)
        return results

BASE_CONTENT_MAPPING = {
    "properties": {
        "object_id": {"type": "integer"},
        "title": {"type": "string"},
        "slug": {"type": "string", "index": "not_analyzed"},
        "subhead": {"type": "string"},
        "description": {"type": "string"},
        "feature_type": {"type": "string"},
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
    def search(self, **kwargs):
        """
        If ElasticSearch is being used, we'll use that for the query, and otherwise
        fall back to Django's .filter().

        Allowed params:

         * query
         * tag(s)?
         * content_type
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

        if kwargs.get('types'):
            results = results.doctypes(*[type_class.get_mapping_type_name() for type_class in kwargs['types']])

        return results.order_by('-published')

    @property
    def tags(self):
        if self._tags:
            return Tagish.search().query(slug__terms=[tag for tag in self._tags.split("\n")])
        return []

    @tags.setter
    def tags(self, value):
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
        self.feature_type = _source['feature_type']
        self.tags = [tag['slug'] for tag in _source['tags']]

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
        }
        if self._tags:
            data['tags'] = [{
                'name': tag_name,
                'slug': slugify(tag_name)
            } for tag_name in self._tags.split("\n")]
        return data
