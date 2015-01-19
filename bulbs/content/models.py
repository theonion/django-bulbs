"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""

import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.db.models import Model
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags
import elasticsearch
from elasticutils import F
from elastimorphic.base import (
    PolymorphicIndexable,
    PolymorphicMappingType,
    SearchManager,
)
from polymorphic import PolymorphicModel
from djbetty import ImageField

from bulbs.content import TagCache
from .shallow import ShallowContentS, ShallowContentResult

try:
    from bulbs.content.tasks import index as index_task  # noqa
    from bulbs.content.tasks import update as update_task  # noqa
    CELERY_ENABLED = True
except ImportError:
    index_task = lambda *x: x
    update_task = lambda *x: x
    CELERY_ENABLED = False


class Tag(PolymorphicIndexable, PolymorphicModel):
    """Model for tagging up Content.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    # additional manager to handle querying with ElasticSearch
    search_objects = SearchManager()

    def __unicode__(self):
        """unicode friendly name
        """
        return '%s: %s' % (self.__class__.__name__, self.name)

    def save(self, *args, **kwargs):
        """sets the `slug` values as the name

        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `super.save()`
        """
        self.slug = slugify(self.name)[:50]
        return super(Tag, self).save(*args, **kwargs)

    def count(self):
        """gets the count of instances saved in the cache

        :return: `int`
        """
        return TagCache.count(self.slug)

    @classmethod
    def get_mapping_properties(cls):
        """provides mapping information for ElasticSearch

        :return: `dict`
        """
        props = super(Tag, cls).get_mapping_properties()
        props.update({
            "name": {"type": "string", "analyzer": "autocomplete"},
            "slug": {"type": "string", "index": "not_analyzed"},
            "type": {"type": "string", "index": "not_analyzed"}
        })
        return props

    def extract_document(self):
        """instantiates a dict representation of the object from ElasticSearch

        :return: `dict`
        """
        data = super(Tag, self).extract_document()
        data.update({
            "name": self.name,
            "slug": self.slug,
            "type": self.get_mapping_type_name()
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        """gets the serializer class for the model

        :return: `rest_framework.serializers.Serializer`
        """
        from .serializers import TagSerializer
        return TagSerializer


class FeatureType(models.Model):
    """
    special model for featured content
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        """unicode friendly name
        """
        return self.name

    def save(self, *args, **kwargs):
        """sets the `slug` values as the name

        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `super.save()`
        """
        if self.slug is None or self.slug == "":
            self.slug = slugify(self.name)
        return super(FeatureType, self).save(*args, **kwargs)


class ContentManager(SearchManager):
    """
    a specialized version of `elastimorphic.base.SearchManager` for `bulbs.content.Content`
    """

    def s(self):
        """Returns a ShallowContentS() instance, using an ES URL from the settings, and an index
        from this manager's model
        """

        base_polymorphic_class = self.model.get_base_class()
        type_ = type(
            '%sMappingType' % base_polymorphic_class.__name__,
            (PolymorphicMappingType,),
            {"base_polymorphic_class": base_polymorphic_class})

        return ShallowContentS(type_=type_).es(urls=settings.ES_URLS)

    def search(self, **kwargs):
        """
        Queries using ElasticSearch, returning an elasticutils queryset.

        :param kwargs: keyword arguments (optional)
         * query : ES Query spec
         * tags : content tags
         * types : content types
         * feature_types : featured types
         * authors : authors
         * published : date range
        """
        results = self.s()

        if "query" in kwargs:
            results = results.query(_all__match=kwargs.get("query"))
        else:
            results = results.order_by('-published', '-last_modified')

        # Right now we have "Before", "After" (datetimes),
        # and "published" (a boolean). Should simplify this in the future.
        if "before" in kwargs or "after" in kwargs:
            if "before" in kwargs:
                results = results.query(published__lte=kwargs["before"], must=True)

            if "after" in kwargs:
                results = results.query(published__gte=kwargs["after"], must=True)
        else:
            # TODO: kill this "published" param. it sucks
            if kwargs.get("published", True) and not "status" in kwargs:
                now = timezone.now()
                results = results.query(published__lte=now, must=True)

        if "status" in kwargs:
            results = results.filter(status=kwargs.get("status"))

        f = F()
        for tag in kwargs.get("tags", []):
            if tag.startswith("-"):
                f &= ~F(**{"tags.slug": tag[1:]})
            else:
                f |= F(**{"tags.slug": tag})

        for feature_type in kwargs.get("feature_types", []):
            if feature_type.startswith("-"):
                f &= ~F(**{"feature_type.slug": feature_type[1:]})
            else:
                f |= F(**{"feature_type.slug": feature_type})

        for author in kwargs.get("authors", []):
            if author.startswith("-"):
                f &= ~F(**{"authors.username": author})
            else:
                f |= F(**{"authors.username": author})

        results = results.filter(f)

        # only use valid subtypes
        types = kwargs.pop("types", [])
        model_types = self.model.get_mapping_type_names()
        if types:
            results = results.doctypes(*[
                type_classname for type_classname
                in types
                if type_classname in model_types
            ])
        else:
            results = results.doctypes(*model_types)
        return results

    def in_bulk(self, pks):
        """performs a GET from ElasticSearch en masse

        :param pks: iterable of object primary keys
        :return: `list`
        """
        results = self.es.multi_get(pks, index=self.model.get_index_name())
        ret = []
        for r in results["docs"]:
            if "_source" in r:
                ret.append(ShallowContentResult(r["_source"]))
            else:
                ret.append(None)
        return ret


class Content(PolymorphicIndexable, PolymorphicModel):
    """
    The base content model from which all other content derives.
    """

    published = models.DateTimeField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, default=timezone.now)
    title = models.CharField(max_length=512)
    slug = models.SlugField(blank=True, default='')
    description = models.TextField(max_length=1024, blank=True, default="")
    # field used if thumbnail has been manually overridden
    thumbnail_override = ImageField(null=True, blank=True, editable=False)
    # attribution
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    feature_type = models.ForeignKey(FeatureType, null=True, blank=True)
    subhead = models.CharField(max_length=255, blank=True, default="")
    # tagging
    tags = models.ManyToManyField(Tag, blank=True)
    # Should this item be indexed?
    indexed = models.BooleanField(default=True)
    # Is this a read only model? (i.e. from elasticsearch)
    _readonly = False
    # custom ES manager
    search_objects = ContentManager()

    class Meta:
        permissions = (
            ("publish_own_content", "Can publish their own content"),
            ("publish_content", "Can publish content"),
            ("promote_content", "Can promote content"),
        )

    def __unicode__(self):
        """unicode friendly name
        """
        return '%s: %s' % (self.__class__.__name__, self.title)

    @property
    def thumbnail(self):
        """Read-only attribute that provides the value of the thumbnail to display.
        """
        # check if there is a valid thumbnail override
        if self.thumbnail_override.id is not None:
            return self.thumbnail_override

        # otherwise, just try to grab the first image
        first_image = self.first_image
        if first_image is not None:
            return first_image

        # no override for thumbnail and no non-none image field, just return override,
        # which is a blank image field
        return self.thumbnail_override

    @property
    def first_image(self):
        """Ready-only attribute that provides the value of the first non-none image that's
        not the thumbnail override field.
        """
        # loop through image fields and grab the first non-none one
        for field in self._meta.fields:
            if isinstance(field, ImageField):
                if field.name is not 'thumbnail_override':
                    field_value = getattr(self, field.name)
                    if field_value.id is not None:
                        return field_value

        # no non-none images, return None
        return None

    def get_absolute_url(self):
        """produces a url to link directly to this instance, given the URL config

        :return: `str`
        """
        try:
            url = reverse("content-detail-view", kwargs={"pk": self.pk, "slug": self.slug})
        except NoReverseMatch:
            url = None
        return url

    def get_status(self):
        """Returns a string representing the status of this item.
        By default, this is one of "draft", "scheduled" or "published".

        :return: `str`
        """
        if self.published:
            return "final"  # The published time has been set
        return "draft"  # No published time has been set

    @property
    def is_published(self):
        """determines if the content is/should be live

        :return: `bool`
        """
        if self.published:
            now = timezone.now()
            if now >= self.published:
                return True
        return False

    @property
    def type(self):
        """gets the ElasticSearch mapping name

        :return: `str`
        """
        return self.get_mapping_type_name()

    def ordered_tags(self):
        """gets the related tags

        :return: `list` of `Tag` instances
        """
        tags = list(self.tags.all())
        return sorted(
            tags,
            key=lambda tag: ((type(tag) != Tag) * 100000) + tag.count(),
            reverse=True
        )

    def build_slug(self):
        """strips tagging from the title

        :return: `str`
        """
        return strip_tags(self.title)

    def save(self, *args, **kwargs):
        """creates the slug, queues up for indexing and saves the instance

        :param args: inline arguments (optional)
        :param kwargs: keyword arguments
        :return: `bulbs.content.Content`
        """
        if not self.slug:
            self.slug = slugify(self.build_slug())[:self._meta.get_field("slug").max_length]
        if self.indexed is False:
            if kwargs is None:
                kwargs = {}
            kwargs["index"] = False
        return super(Content, self).save(*args, **kwargs)

    # class methods ##############################
    @classmethod
    def get_mapping_properties(cls):
        """creates the mapping for ElasticSearch

        :return: `dict`
        """
        properties = super(Content, cls).get_mapping_properties()
        properties.update({
            "published": {"type": "date"},
            "last_modified": {"type": "date"},
            "title": {"type": "string", "analyzer": "snowball", "_boost": 2.0},
            "slug": {"type": "string"},
            "description": {"type": "string", },
            "thumbnail": {"type": "integer"},
            "feature_type": {
                "properties": {
                    "name": {
                        "type": "multi_field",
                        "fields": {
                            "name": {"type": "string", "index": "not_analyzed"},
                            "autocomplete": {"type": "string", "analyzer": "autocomplete"}
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
            "absolute_url": {"type": "string"},
            "status": {"type": "string", "index": "not_analyzed"}
        })
        return properties

    def extract_document(self):
        """maps data returned from ElasticSearch into a dict for instantiating an object

        :return: `dict`
        """
        data = super(Content, self).extract_document()
        data.update({
            "published": self.published,
            "last_modified": self.last_modified,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "thumbnail": self.thumbnail.id if self.thumbnail else None,
            "authors": [
                {
                    "first_name": author.first_name,
                    "id": author.id,
                    "last_name": author.last_name,
                    "username": author.username
                }
                for author in self.authors.all()
            ],
            "tags": [tag.extract_document() for tag in self.ordered_tags()],
            "absolute_url": self.get_absolute_url(),
            "status": self.get_status()
        })
        if self.feature_type:
            data["feature_type"] = {
                "name": self.feature_type.name,
                "slug": self.feature_type.slug
            }
        return data

    @classmethod
    def get_serializer_class(cls):
        """gets the serializer for the class

        :return: `rest_framework.serializers.Serializer`
        """
        from .serializers import ContentSerializer
        return ContentSerializer


class LogEntryManager(models.Manager):
    """
    provides additional manager methods for `bulbs.content.LogEntry` model
    """

    def log(self, user, content, message):
        """creates a new log record

        :param user: user
        :param content: content instance
        :param message: change information
        """
        return self.create(
            user=user,
            content_type=ContentType.objects.get_for_model(content),
            object_id=content.pk,
            change_message=message
        )


class LogEntry(models.Model):
    """
    log entries for changes to content
    """

    action_time = models.DateTimeField("action time", auto_now=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name="change_logs")
    object_id = models.TextField("object id", blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="change_logs")
    change_message = models.TextField("change message", blank=True)
    # custom manager
    objects = LogEntryManager()

    class Meta:
        ordering = ("-action_time",)


class ObfuscatedUrlInfo(Model):
    """
    Stores info used for obfuscated urls of unpublished content.
    """

    content = models.ForeignKey(Content)
    create_date = models.DateTimeField()
    expire_date = models.DateTimeField()
    url_uuid = models.CharField(max_length=32, unique=True, editable=False)

    def save(self, *args, **kwargs):
        """sets uuid for url

        :param args: inline arguments (optional)
        :param kwargs: keyword arguments (optional)
        :return: `super.save()`
        """
        if not self.id:  # this is a totally new instance, create uuid value
            self.url_uuid = str(uuid.uuid4()).replace("-", "")
        super(ObfuscatedUrlInfo, self).save(*args, **kwargs)


##
# signal functions

def content_deleted(sender, instance=None, **kwargs):
    """removes content from the ES index when deleted from DB
    """
    if getattr(instance, "_index", True):
        index = instance.get_index_name()
        klass = instance.get_real_instance_class()
        try:
            klass.search_objects.es.delete(index, klass.get_mapping_type_name(), instance.id)
        except elasticsearch.exceptions.NotFoundError:
            pass


##
# signal hooks

models.signals.pre_delete.connect(content_deleted, Content)
