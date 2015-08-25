"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""

import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.db.models import Model
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags
from djes.models import Indexable, IndexableManager
from elasticsearch_dsl import field
from polymorphic import PolymorphicModel, PolymorphicManager
from djbetty import ImageField

from bulbs.content import TagCache
from .filters import Authors, Published, Status, Tags, FeatureTypes

try:
    from bulbs.content.tasks import index as index_task  # noqa
    CELERY_ENABLED = True
except ImportError:
    index_task = lambda *x: x
    CELERY_ENABLED = False


class ElasticsearchImageField(field.Integer):

    def to_es(self, data):
        return data.id


class TagManager(PolymorphicManager, IndexableManager):
    pass


class Tag(PolymorphicModel, Indexable):
    """Model for tagging up Content.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Mapping:
        name = field.String(analyzer="autocomplete", fields={"raw": field.String(index="not_analyzed")})

    search_objects = TagManager()

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
    def get_serializer_class(cls):
        """gets the serializer class for the model

        :return: `rest_framework.serializers.Serializer`
        """
        from .serializers import TagSerializer
        return TagSerializer


class FeatureType(Indexable):
    """
    special model for featured content
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Mapping:
        name = field.String(analyzer="autocomplete", fields={"raw": field.String(index="not_analyzed")})
        slug = field.String(index="not_analyzed")

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


class TemplateType(models.Model):
    """
    Template type for Content.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content_type = models.ForeignKey(ContentType)


class ContentManager(PolymorphicManager, IndexableManager):
    """
    a specialized version of `djes.models.SearchManager` for `bulbs.content.Content`
    """

    # def __getattr__(self, name):
    #     if name.startswith('__'):
    #         return super(PolymorphicManager, self).__getattr__(self, name)
    #     return getattr(self.all(), name)

    def search(self, **kwargs):
        """
        Queries using ElasticSearch, returning an elasticsearch queryset.

        :param kwargs: keyword arguments (optional)
         * query : ES Query spec
         * tags : content tags
         * types : content types
         * feature_types : featured types
         * published : date range
        """
        search_query = super(ContentManager, self).search()

        if "query" in kwargs:
            search_query = search_query.query("match", _all=kwargs.get("query"))
        else:
            search_query = search_query.sort('-published', '-last_modified')

        # Right now we have "Before", "After" (datetimes),
        # and "published" (a boolean). Should simplify this in the future.
        if "before" in kwargs or "after" in kwargs:
            published_filter = Published(before=kwargs.get("before"), after=kwargs.get("after"))
            search_query = search_query.filter(published_filter)
        else:
            # TODO: kill this "published" param. it sucks
            if kwargs.get("published", True) and "status" not in kwargs:
                published_filter = Published()
                search_query = search_query.filter(published_filter)

        if "status" in kwargs:
            search_query = search_query.filter(Status(kwargs["status"]))

        tag_filter = Tags(kwargs.get("tags", []))
        search_query = search_query.filter(tag_filter)

        author_filter = Authors(kwargs.get("authors", []))
        search_query = search_query.filter(author_filter)

        feature_type_filter = FeatureTypes(kwargs.get("feature_types", []))
        search_query = search_query.filter(feature_type_filter)

        # Is this good enough? Are we even using this feature at all?
        types = kwargs.pop("types", [])
        if types:
            search_query._doc_type = types
        return search_query


class Content(PolymorphicModel, Indexable):
    """
    The base content model from which all other content derives.
    """

    published = models.DateTimeField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=512)
    slug = models.SlugField(blank=True, default='')
    template_type = models.ForeignKey(TemplateType, blank=True, null=True)
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

    class Mapping:
        pk = field.Integer()
        title = field.String(analyzer="snowball", _boost=2.0)
        slug = field.String(index="not_analyzed")
        status = field.String(index="not_analyzed")
        thumbnail_override = ElasticsearchImageField()

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
        for model_field in self._meta.fields:
            if isinstance(model_field, ImageField):
                if model_field.name is not 'thumbnail_override':
                    field_value = getattr(self, model_field.name)
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
    status = property(get_status)

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
        cls = instance.get_real_instance_class()
        index = cls.search_objects.mapping.index
        doc_type = cls.search_objects.mapping.doc_type

        cls.search_objects.client.delete(index, doc_type, instance.id, ignore=[404])


##
# signal hooks

models.signals.pre_delete.connect(content_deleted, Content)
