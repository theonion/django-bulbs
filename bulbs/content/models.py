"""Base models for "Content", including the indexing and search features
that we want any piece of content to have."""

import logging
import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.db.models import Model
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import strip_tags

from djbetty import ImageField
from djes.models import Indexable, IndexableManager
from elasticsearch import TransportError
from elasticsearch_dsl import field
from polymorphic import PolymorphicModel, PolymorphicManager

from bulbs.content import TagCache
from bulbs.content.tasks import (
    index_content_contributions, index_content_report_content_proxy,
    index_feature_type_content
)
from bulbs.utils.methods import datetime_to_epoch_seconds, get_template_choices
from .managers import ContentManager


logger = logging.getLogger(__name__)


TEMPLATE_CHOICES = get_template_choices()


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
        name = field.String(
            analyzer="autocomplete", fields={"raw": field.String(index="not_analyzed")}
        )

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
    instant_article = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(FeatureType, self).__init__(*args, **kwargs)
        # Reference for state change on save.
        self._db_instant_article = self.instant_article

    class Mapping:
        name = field.String(
            analyzer="autocomplete", fields={"raw": field.String(index="not_analyzed")}
        )
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
        feature_type = super(FeatureType, self).save(*args, **kwargs)
        if self.instant_article_is_dirty:
            index_feature_type_content.delay(self.pk)
        self._db_instant_article = self.instant_article
        return feature_type

    @property
    def instant_article_is_dirty(self):
        return bool(self.instant_article != self._db_instant_article)


class TemplateType(models.Model):

    """
    Template type for Content.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content_type = models.ForeignKey(ContentType)


def _percolate(index, doc_type, content_id, body):
    try:
        results = Content.search_objects.client.percolate(index=index,
                                                          doc_type=doc_type,
                                                          id=content_id,
                                                          body=body)
    except TransportError:
        logger.exception('Percolator error: Content ID %s, %s', content_id, body)
        return []

    # Log any errors (but still try to return any results)
    if results.get('_shards', {}).get('failures'):
        logger.error('Elasticsearch error: %s', results.get('_shards'))

    if results["total"] > 0:
        return results['matches']
    else:
        return []


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
    # Is this content always fresh / relevant?
    evergreen = models.BooleanField(default=False)
    # Is this a read only model? (i.e. from elasticsearch)
    _readonly = False
    instant_article = models.BooleanField(default=False)
    # Tunic Campaign ID
    # NOTE: Don't want to accidentally overwrite derived model campaign_id fields during migration
    # Will rename to "campaign_id" after migration
    tunic_campaign_id = models.IntegerField(blank=True, null=True, default=None)
    # Custom template choice. Configured via BULBS_TEMPLATE_CHOICE
    template_choice = models.IntegerField(default=0, choices=TEMPLATE_CHOICES)

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
    def es_type(self):
        return "{}_{}".format(
            self._meta.app_label, self._meta.model_name.replace("_elasticsearchresult", "")
        )

    @property
    def type(self):
        # TODO: This is to be removed, but some sites rely on it's existence currently.
        return self.es_type

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

    def get_targeting(self):
        data = {
            "dfp_feature": getattr(self.feature_type, "slug", None),
            "dfp_contentid": self.pk,
            "dfp_pagetype": self.__class__.__name__.lower(),
            "dfp_slug": self.slug,
            "dfp_evergreen": self.evergreen,
            "dfp_title": strip_tags(self.title),
            "dfp_site": getattr(settings, "DFP_SITE", None)
        }
        if self.published is not None:
            data["dfp_publishdate"] = self.published.isoformat()
        data["dfp_campaign"] = getattr(self, "campaign", None)
        tags = self.ordered_tags()
        data["dfp_section"] = tags[0].slug if tags else None
        return data

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
        content = super(Content, self).save(*args, **kwargs)
        index_content_contributions.delay(self.id)
        index_content_report_content_proxy.delay(self.id)
        return content

    @classmethod
    def get_serializer_class(cls):
        """gets the serializer for the class

        :return: `rest_framework.serializers.Serializer`
        """
        from .serializers import ContentSerializer
        return ContentSerializer

    def get_template_name(self):
        return dict(TEMPLATE_CHOICES).get(self.template_choice)

    def percolate_special_coverage(self, max_size=10, sponsored_only=False):

        """gets list of active, sponsored special coverages containing this content via
        Elasticsearch Percolator (see SpecialCoverage._save_percolator)

        Sorting:
            1) Manually added
            2) Most recent start date
        """

        # Elasticsearch v1.4 percolator range query does not support DateTime range queries
        # (PercolateContext.nowInMillisImpl is not implemented). Once using
        # v1.6+ we can instead compare "start_date/end_date" to python DateTime
        now_epoch = datetime_to_epoch_seconds(timezone.now())

        MANUALLY_ADDED_BOOST = 10
        SPONSORED_BOOST = 100  # Must be order of magnitude higher than "Manual" boost

        # Unsponsored boosting to either lower priority or exclude
        if sponsored_only:
            # Omit unsponsored
            unsponsored_boost = 0
        else:
            # Below sponsored (inverse boost, since we're filtering on "sponsored=False"
            unsponsored_boost = (1.0 / SPONSORED_BOOST)

        # ES v1.4 has more limited percolator capabilities than later
        # implementations. As such, in order to get this to work, we need to
        # sort via scoring_functions, and then manually filter out zero scores.
        sponsored_filter = {
            "query": {
                "function_score": {
                    "functions": [

                        # Boost Recent Special Coverage
                        # Base score is start time
                        # Note: ES 1.4 sorting granularity is poor for times
                        # within 1 hour of each other.
                        {

                            # v1.4 "field_value_factor" does not yet support
                            # "missing" param, and so must filter on whether
                            # "start_date" field exists.
                            "filter": {
                                "exists": {
                                    "field": "start_date",
                                },
                            },
                            "field_value_factor": {
                                "field": "start_date",
                            }
                        },
                        {
                            # Related to above, if "start_date" not found, omit
                            # via zero score.
                            "filter": {
                                "not": {
                                    "exists": {
                                        "field": "start_date",
                                    },
                                },
                            },
                            "weight": 0,
                        },


                        # Ignore non-special-coverage percolator entries
                        {
                            "filter": {
                                "not": {
                                    "prefix": {"_id": "specialcoverage"},
                                },
                            },
                            "weight": 0,
                        },

                        # Boost Manually Added Content
                        {
                            "filter": {
                                "terms": {
                                    "included_ids": [self.id],
                                }
                            },
                            "weight": MANUALLY_ADDED_BOOST,
                        },
                        # Penalize Inactive (Zero Score Will be Omitted)
                        {
                            "filter": {
                                "or": [
                                    {
                                        "range": {
                                            "start_date_epoch": {
                                                "gt": now_epoch,
                                            },
                                        }
                                    },
                                    {
                                        "range": {
                                            "end_date_epoch": {
                                                "lte": now_epoch,
                                            },
                                        }
                                    },
                                ],
                            },
                            "weight": 0,
                        },
                        # Penalize Unsponsored (will either exclude or lower
                        # based on "sponsored_only" flag)
                        {
                            "filter": {
                                "term": {
                                    "sponsored": False,
                                }
                            },
                            "weight": unsponsored_boost,
                        },
                    ],
                },
            },

            "sort": "_score",  # The only sort method supported by ES v1.4 percolator
            "size": max_size,  # Required for sort
        }

        results = _percolate(index=self.mapping.index,
                             doc_type=self.mapping.doc_type,
                             content_id=self.id,
                             body=sponsored_filter)

        return [r["_id"] for r in results
                # Zero score used to omit results via scoring function (ex: inactive)
                if r['_score'] > 0]


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
