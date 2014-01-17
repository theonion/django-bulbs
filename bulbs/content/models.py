"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.db.backends import util
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags

from bulbs.content import TagCache
from bulbs.images.fields import RemoteImageField
from bulbs.indexable.indexable import PolymorphicIndexable, SearchManager, PolymorphicMappingType
from elasticutils import SearchResults, S
from elasticutils.contrib.django import get_es
from polymorphic import PolymorphicModel, PolymorphicManager

from .shallow import ShallowContentS, ShallowContentResult

try:
    from bulbs.content.tasks import index as index_task
    from bulbs.content.tasks import update as update_task
    CELERY_ENABLED = True
except ImportError:
    CELERY_ENABLED = False


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
        id_facet_counts = self.facet_counts().get("id", None)
        if id_facet_counts is None:
            raise ValueError('No id facets found.')
        # the facet "term" is the id. let's get a list of those.
        ids = [fc["term"] for fc in id_facet_counts]
        models = fetch_cached_models_by_id(model_class, ids)
        # annotate models with facet counts
        for model, facet_result in zip(models, id_facet_counts):
            model.facet_count = facet_result["count"]
        return models


class ModelSearchResults(SearchResults):
    """Takes the "id" list returned by a ModelS and delivers model instances."""
    @classmethod
    def get_model(cls):
        raise NotImplementedError('ModelSearchResults requires a `get_model` method.')
        
    def set_objects(self, results):
        ids = list(int(r["_id"]) for r in results)
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
        self.steps.append(("values_list", ["_id"]))

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


class TagSearchResults(ModelSearchResults):
    @classmethod
    def get_model(cls):
        return Tag


class TagS(ModelS):
    results_class = TagSearchResults


class TagManager(PolymorphicManager):
    def search(self, s_class=TagS, **kwargs):
        """Search tags...profit."""
        index = self.model.get_index_name()
        results = s_class().es(urls=settings.ES_URLS).indexes(index)
        name = kwargs.pop("query", '')
        if name:
            results = results.query(name__match=name, should=True)

        types = kwargs.pop("types", [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*[
                type_classname for type_classname in types \
                if type_classname in self.model.get_mapping_type_names()
            ])
        else:
            results = results.doctypes(*self.model.get_mapping_type_names())
        return results


class Tag(PolymorphicIndexable, PolymorphicModel):
    """Model for tagging up Content."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    objects = TagManager()
    search_objects = SearchManager()

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    def count(self):
        return TagCache.count(self.slug)

    @classmethod
    def get_mapping_properties(cls):
        props = super(Tag, cls).get_mapping_properties()
        props.update({
            "name": {"type": "string", "analyzer": "autocomplete"},
            "slug": {"type": "string", "index": "not_analyzed"},
            "type": {"type": "string", "index": "not_analyzed"}
        })
        return props
    
    def extract_document(self):
        data = super(Tag, self).extract_document()
        data.update({
            "name": self.name,
            "slug": self.slug,
            "type": self.get_mapping_type_name()
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        from .serializers import TagSerializer
        return TagSerializer


class ContentManager(SearchManager):

    def s(self):
        """Returns a ShallowContentS() instance, using an ES URL from the settings, and an index
        from this manager's model"""

        base_polymorphic_class = self.model.get_base_class()
        type_ = type('%sMappingType' % base_polymorphic_class.__name__, (PolymorphicMappingType,), {"base_polymorphic_class": base_polymorphic_class})

        return ShallowContentS(type_=type_).es(urls=settings.ES_URLS)

    def search(self, **kwargs):
        """
        Queries using ElasticSearch, returning an elasticutils queryset.

        Allowed params:

         * query
         * tags
         * types
         * feature_types
         * authors
         * published
        """
        
        results = self.s()

        if "query" in kwargs:
            results = results.query(_all__match=kwargs.get("query"))

        # Right now we have "Before", "After" (datetimes), and "published" (a boolean). Should simplify this in the future.
        if "before" in kwargs or "after" in kwargs:
            if "before" in kwargs:
                results = results.query(published__lte=kwargs["before"], must=True)

            if "after" in kwargs:
                results = results.query(published__gte=kwargs["after"], must=True)
        else:
            if kwargs.get("published", True):
                now = timezone.now()
                results = results.query(published__lte=now, must=True)

        if "tags" in kwargs:
            tags = kwargs["tags"]
            results = results.filter(**{'tags.slug__in':tags})

        if "feature_types" in kwargs:
            feature_types = kwargs["feature_types"]
            results = results.filter(**{'feature_type.slug__in':feature_types})

        if "authors" in kwargs:
            authors = kwargs["authors"]
            results = results.filter(**{'authors.username__in':authors})

        types = kwargs.pop("types", [])
        if types:
            # only use valid subtypes
            results = results.doctypes(*types)

        return results.order_by('-published')

    def in_bulk(self, pks):
        results = self.es.multi_get(pks, index=self.model.get_index_name())
        ret = []
        for r in results["docs"]:
            if "_source" in r:
                ret.append(ShallowContentResult(r["_source"]))
            else:
                ret.append(None)
        return ret


class Content(PolymorphicIndexable, PolymorphicModel):
    """The base content model from which all other content derives."""
    published = models.DateTimeField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, default=timezone.now)
    title = models.CharField(max_length=512)
    slug = models.SlugField(blank=True, default='')
    description = models.TextField(max_length=1024, blank=True, default='')
    image = RemoteImageField(null=True, blank=True)
    
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    indexed = models.BooleanField(default=True) # Should this item be indexed? 

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)

    search_objects = ContentManager()

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        try:
            url = reverse('content-detail-view', kwargs={"pk": self.pk, "slug": self.slug})
        except NoReverseMatch:
            url = None
        return url

    @property
    def is_published(self):
        if self.published:
            now = timezone.now()
            if now >= self.published:
                return True
        return False

    @property
    def type(self):
        return self.get_mapping_type_name()

    @property
    def byline(self):
        # If we have authors, just put them in a list
        if self.authors.exists():
            return ', '.join([user.get_full_name() for user in self.authors.all()])

        # Well, shit. I guess there's no byline.
        return None

    def ordered_tags(self):
        tags = list(self.tags.all())
        return sorted(tags, key=lambda tag: ((type(tag) != Tag) * 100000) + tag.count(), reverse=True)

    @property
    def feature_type_slug(self):
        return slugify(self.feature_type)

    def build_slug(self):
        return strip_tags(self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.build_slug())[:self._meta.get_field("slug").max_length]
        if self.indexed is False:
            if kwargs is None:
                kwargs = {}
            kwargs['index'] = False
        return super(Content, self).save(*args, **kwargs)

    # class methods ##############################
    @classmethod
    def get_mapping_properties(cls):
        properties = super(Content, cls).get_mapping_properties()
        properties.update({
            "published": {"type": "date"},
            "last_modified": {"type": "date"},
            "title": {"type": "string", "analyzer":"snowball", "_boost":  2.0},
            "slug": {"type": "string"},
            "description": {"type": "string",},
            "image": {"type": "string"},
            "feature_type": {
                "properties": {
                    "name": {
                        "type": "multi_field",
                        "fields": {
                            "name" : {"type": "string", "index": "not_analyzed"},
                            "autocomplete" : {"type": "string", "analyzer": "autocomplete"}
                        }
                    },
                    "slug": {"type": "string", "index": "not_analyzed"}
                }
            },
            "authors": {
                "properties": {
                    "first_name": {"type": "string"},
                    "id": {"type": "long"},
                    "last_name": {"type": "string"},
                    "username": {"type": "string", "index": "not_analyzed"}
                }
            },
            "tags": {
                "properties": Tag.get_mapping_properties()
            },
            "absolute_url": {"type": "string"}
        })
        return properties

    def extract_document(self):
        data = super(Content, self).extract_document()
        data.update({
            "published"        : self.published,
            "last_modified"    : self.last_modified,
            "title"            : self.title,
            "slug"             : self.slug,
            "description"      : self.description,
            "image"            : self.image.id if self.image else None,
            "feature_type"     : {
                "name": self.feature_type,
                "slug": slugify(self.feature_type)
            },
            "authors": [{
                "first_name": author.first_name,
                "id"        : author.id,
                "last_name" : author.last_name,
                "username"  : author.username
            } for author in self.authors.all()],
            "tags": [tag.extract_document() for tag in self.ordered_tags()],
            "absolute_url": self.get_absolute_url()
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ContentSerializer
        return ContentSerializer


class LogEntry(models.Model):
    action_time = models.DateTimeField('action time', auto_now=True)
    content = models.ForeignKey(Content, related_name='change_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='change_logs')
    change_message = models.TextField('change message', blank=True)

    class Meta:
        ordering = ('-action_time',)


def content_deleted(sender, instance=None, **kwargs):
    if getattr(instance, "_index", True):
        es = get_es()
        index = instance.get_index_name()
        klass = instance.get_real_instance_class()
        es.delete(index, klass.get_mapping_type_name(), instance.id)


models.signals.pre_delete.connect(content_deleted, Content)

