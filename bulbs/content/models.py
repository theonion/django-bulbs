"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags

from bulbs.content import TagCache
from elasticutils import SearchResults, S, F
from elasticutils.contrib.django import get_es
from elastimorphic.base import (
    PolymorphicIndexable,
    PolymorphicMappingType,
    SearchManager,
)
from polymorphic import PolymorphicModel, PolymorphicManager

from .shallow import ShallowContentS, ShallowContentResult

from djbetty import ImageField

try:
    from bulbs.content.tasks import index as index_task  # noqa
    from bulbs.content.tasks import update as update_task  # noqa
    CELERY_ENABLED = True
except ImportError:
    CELERY_ENABLED = False


class Tag(PolymorphicIndexable, PolymorphicModel):
    """Model for tagging up Content."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

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
        type_ = type(
            '%sMappingType' % base_polymorphic_class.__name__,
            (PolymorphicMappingType,),
            {"base_polymorphic_class": base_polymorphic_class})

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
            if kwargs.get("published", True) and not "status" in kwargs:  # TODO: kill this "published" param. it sucks
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
                type_classname for type_classname in types \
                if type_classname in model_types
            ])
        else:
            results = results.doctypes(*model_types)
        return results

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
    image = ImageField(null=True, blank=True)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    feature_type = models.CharField(max_length=255, null=True, blank=True)  # "New in Brief", "Newswire", etc.
    subhead = models.CharField(max_length=255, null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    indexed = models.BooleanField(default=True)  # Should this item be indexed?

    _readonly = False  # Is this a read only model? (i.e. from elasticsearch)

    search_objects = ContentManager()

    def __unicode__(self):
        return '%s: %s' % (self.__class__.__name__, self.title)

    def get_absolute_url(self):
        try:
            url = reverse("content-detail-view", kwargs={"pk": self.pk, "slug": self.slug})
        except NoReverseMatch:
            url = None
        return url

    def get_status(self):
        """Returns a string representing the status of this item

        By default, this is one of "draft", "scheduled" or "published"."""

        if self.published:
            return "final"  # The published time has been set

        return "draft"  # No published time has been set

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

    def ordered_tags(self):
        tags = list(self.tags.all())
        return sorted(
            tags, key=lambda tag: ((type(tag) != Tag) * 100000) + tag.count(), reverse=True)

    def build_slug(self):
        return strip_tags(self.title)

    def save(self, *args, **kwargs):
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
        properties = super(Content, cls).get_mapping_properties()
        properties.update({
            "published": {"type": "date"},
            "last_modified": {"type": "date"},
            "title": {"type": "string", "analyzer": "snowball", "_boost": 2.0},
            "slug": {"type": "string"},
            "description": {"type": "string", },
            "image": {"type": "string"},
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
            "absolute_url": self.get_absolute_url(),
            "status": self.get_status()
        })
        return data

    @classmethod
    def get_serializer_class(cls):
        from .serializers import ContentSerializer
        return ContentSerializer


class LogEntryManager(models.Manager):
    def log(self, user, content, message):
        return self.create(
            user=user,
            content_type=ContentType.objects.get_for_model(content),
            object_id=content.pk,
            change_message=message
        )


class LogEntry(models.Model):
    action_time = models.DateTimeField("action time", auto_now=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name="change_logs")
    object_id = models.TextField(("object id"), blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="change_logs")
    change_message = models.TextField("change message", blank=True)

    objects = LogEntryManager()

    class Meta:
        ordering = ("-action_time",)


def content_deleted(sender, instance=None, **kwargs):
    if getattr(instance, "_index", True):
        index = instance.get_index_name()
        klass = instance.get_real_instance_class()
        klass.search_objects.es.delete(index, klass.get_mapping_type_name(), instance.id)


models.signals.pre_delete.connect(content_deleted, Content)
