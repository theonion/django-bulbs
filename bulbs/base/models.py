import rawes

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import m2m_changed


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ContentQuerySet(object):

    def __init__(self, published=True, content_type=None, tags=[]):
        self.published = published
        self.tags = tags
        self.content_type = content_type

    def data(self):
        must = []
        if self.published:
            must.append(self.published)

        if self.tags:
            must.append(self.tags)

        if self.content_type:
            must.append(self.content_type)

        search_data = {
            'query': {
                'bool': {
                    'must': must
                },
            }
        }
        return search_data

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = None
        if type(value) is str:
            self._content_type = {
                'term': {
                    'content_type': value
                }
            }
        elif value is not None:
            self._content_type = {
                'terms': {
                    'content_type': value,
                    'minimum_match': 1
                }
            }

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        # TODO: Test for actual Tag() objects
        self._tags = []
        for tag in value:
            self._tags.append({
                'term': {
                    "tag": tag,
                }
            })

    @property
    def published(self):
        return self._published

    @published.setter
    def published(self, value):
        if value is True:
            self._published = {
                'range': {
                    'published': {
                        'to': timezone.now(),
                    }
                }
            }
        if value is False:
            self._published = {
                'range': {
                    'published': {
                        'from': timezone.now(),
                    }
                }
            }
        # TODO: Test for datetime


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

        es = rawes.Elastic(**settings.ES_SERVER)  # TODO: Connection pooling

        query = ContentQuerySet(**kwargs)
        import pprint
        pprint.pprint(query.data())
        results = es.get('content/_search', data=query.data())
        return results

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
    published = models.DateTimeField(null=True, blank=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.CharField(max_length=510)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)

    _subhead = models.CharField(max_length=255, null=True, blank=True)

    tags = models.ManyToManyField(Tag)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    body = generic.GenericForeignKey('content_type', 'object_id')

    objects = ContentManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        content_class = self.content_type.model_class()
        return content_class.get_content_url(self) or self.body.get_absolute_url()

    def byline(self):

        # If the delegate has customized how the Byline is generated, we'll use that.
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

    def subhead(self):
        content_class = self.content_type.model_class()
        if hasattr(content_class, "subhead"):
            return content_class.subhead(self)
        return self._subhead

    def save(self, *args, **kwargs):
        super(Content, self).save(*args, **kwargs)
        es = rawes.Elastic(**settings.ES_SERVER)
        es_data = {
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'byline': self.byline(),
            'subhead': self.subhead(),
            'published': self.published,
            'content_type': '%s-%s' % (self.content_type.app_label, self.content_type.model),
        }
        if self.tags.exists():
            es_data['tags'] = list(self.tags.values_list('name', flat=True))
        es.put('content/%d' % self.pk, data=es_data)

    class Meta:
        unique_together = (('content_type', 'object_id'),)  # sets up a one-one-relationship between this and a child content object
        verbose_name_plural = "content"


def tags_changed(sender, instance, action, model, **kwargs):
    es = rawes.Elastic(**settings.ES_SERVER)

    if action == "post_add" and instance.tags.exists():
        es_data = es.get('content/%d' % instance.pk)['_source']
        es_data['tags'] = list(instance.tags.values_list('name', flat=True))
        es.put('content/%d' % instance.pk, data=es_data)
m2m_changed.connect(tags_changed, sender=Content.tags.through)


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

    def save(self, *args, **kwargs):
        # TODO: wrap this in a transaction
        super(ContentBody, self).save(*args, **kwargs)
        if self.head:
            ignore_fields = ['tags', 'authors', 'content_type', self.head._meta.pk.attname]
            for name in Content._meta.get_all_field_names():
                if name in ignore_fields:
                    continue
                value = getattr(self, name)
                setattr(self.head, name, value)
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
