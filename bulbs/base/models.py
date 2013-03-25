import rawes
import logging

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone, six

from bulbs.images.models import Image
from bulbs.base.query import ElasticQuerySet


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(Image, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)
        es = rawes.Elastic(**settings.ES_SERVER)
        es_data = {
            'name': self.name,
            'description': self.description,
        }
        es.put('tag/%d' % self.pk, data=es_data)

    def __unicode__(self):
        return self.name


class ContentManager(models.Manager):

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

        return ElasticQuerySet(Content)

    def tagged_as(self, *tag_names):
        """
        Return content that's been tagged with tags of the specified names.

        For example:

            Content.objects.tagged_as("tag1", "tag2")

        Will return objects tagged with tags named 'tag1' OR 'tag2.'
        """
        if tag_names:
            return super(ContentManager, self).get_query_set().filter(tags__name__in=tag_names).distinct()
        else:
            return super(ContentManager, self).get_query_set()

    def only_type(self, cls_or_instance):
        """
        Only return content of the specified type.

        For example:

            Content.objects.only_type(TestContentObj).filter(author="mbone")
        """
        return super(ContentManager, self).filter(content_type=ContentType.objects.get_for_model(cls_or_instance))


class Content(models.Model):
    """
    Base Content object.

    This object includes all the "head" data.

    """
    HEAD_FIELDS = ['published', 'title', 'subhead', 'slug', 'description', 'byline', 'tags', 'feature_type', 'content_type', 'object_id']

    published = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    subhead = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=510)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)
    _tags = models.TextField(null=True, blank=True)
    _feature_type = models.CharField(max_length=255, null=True, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    body = generic.GenericForeignKey('content_type', 'object_id')

    objects = ContentManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        content_class = self.content_type.model_class()
        return content_class.get_content_url(self) or self.body.get_absolute_url()

    @property
    def tags(self):
        if self._tags:
            return [tag.strip().lower() for tag in self._tags.split(",")]
        return None

    @tags.setter
    def tags(self, value):
        # TODO: is this too terrible? Should a setter really have this behavior? Too implicit?
        if isinstance(value, basestring):
            self._tags = ",".join([tag.strip().lower() for tag in self._tags.split(",")])
        else:
            self._tags = ",".join([tag.strip().lower() for tag in value])

    @property
    def byline(self):
        # If the body has customized how the Byline is generated, we'll use that.
        content_class = self.content_type.model_class()
        if hasattr(content_class, "byline"):
            return content_class.byline(self)

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
        # If the body has customized how the Byline is generated, we'll use that.
        content_class = self.content_type.model_class()
        if hasattr(content_class, "feature_type"):
            return content_class.feature_type(self)

        if self._feature_type:
            return self._feature_type

        return None

    @feature_type.setter
    def feature_type(self, value):
        self._feature_type = value

    def save(self, *args, **kwargs):
        super(Content, self).save(*args, **kwargs)
        es = rawes.Elastic(**settings.ES_SERVER)
        es_data = {
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'byline': self.byline,
            'subhead': self.subhead,
            'published': self.published,
            'feature_type': self.feature_type,
            'tags': self.tags,
            'content_type': '%s-%s' % (self.content_type.app_label, self.content_type.model),
            'object_id': self.object_id
        }
        es.put('content/%d' % self.pk, data=es_data)

    class Meta:
        unique_together = (('content_type', 'object_id'),)  # sets up a one-one-relationship between this and a child content object
        verbose_name_plural = "content"


class ContentDelegateManager(models.Manager):

    def create(self, **kwargs):
        """
        Create the delegate object and the parent content object.

        Pass all the regular kwargs you'd like to this method and pass kwargs to the parent Content object by prefixing
        them with `content__`. For example:

            TestContentObj.create_content(field1="my field one",
                                          field2="my field two",
                                          content__title="my title")

        Creates a `TestContentObj` instance first with the fields you'd expect, AND a `Content` instance tied to the
        `TestContentObj` instance that's just been created.
        """

        obj = self.model()
        obj._head = Content()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save(force_insert=True)

        return obj


class ContentBody(models.Model):
    """
    Mixin for objects that'd like to be considered 'content.'
    """

    class Meta:
        abstract = True

    objects = ContentDelegateManager()

    def __getattr__(self, name):
        if name == '_head':
            return None
        return self.head.__getattribute__(name)

    def __unicode__(self):
        return "<%s: #%s>" % (self.__class__.__name__, self.pk)

    def save(self, *args, **kwargs):
        # TODO: wrap this in a transaction
        super(ContentBody, self).save(*args, **kwargs)
        if self.head:
            for name in Content.HEAD_FIELDS:
                try:
                    value = object.__getattribute__(self, name)
                    setattr(self.head, name, value)
                except AttributeError:
                    continue
            self.head.content_type = ContentType.objects.get_for_model(self.__class__)
            self.head.object_id = self.pk
            self.head.save(force_insert=kwargs.get('force_insert', False))

    @staticmethod
    def get_content_url(content):
        return None

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    @property
    def head(self):
        if self._head:
            return self._head

        try:
            self._head = Content.objects.get(object_id=self.pk, content_type=ContentType.objects.get_for_model(self).id)
            return self._head
        except Content.DoesNotExist:
            return None
