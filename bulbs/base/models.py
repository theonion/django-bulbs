import rawes

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=255)

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

        self.es = rawes.Elastic(**settings.ES_SERVER)  # TODO: Connection pooling

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

    This object includes all shared data.

    """
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.CharField(max_length=510)

    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    _byline = models.CharField(max_length=255, null=True, blank=True)

    _subhead = models.CharField(max_length=255, null=True, blank=True)  # NY Times calls this a "kicker"? This would probably be used as a "feature type".

    tags = models.ManyToManyField(Tag)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = ContentManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        content_class = self.content_type.model_class()
        return content_class.get_content_url(self) or self.content_object.get_absolute_url()

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
            'created': self.created,
            'modified': self.modified,
            'content_type': '%s-%s' % (self.content_type.app_label, self.content_type.model),
        }
        es.put('content/%d' % self.id, data=es_data)

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

        content_keys = ['title', 'slug', 'description', 'byline', 'subhead']  # The keys you want
        content_kwargs = {}
        for key in content_keys:
            if key in kwargs:
                content_kwargs[key] = kwargs[key]
                del kwargs[key]

        tags = []
        if 'tags' in kwargs:
            tags = kwargs["tags"]
            del kwargs["tags"]


        obj_instance = super(ContentDelegateManager, self).create(**kwargs)
        content_kwargs.update({'content_type': ContentType.objects.get_for_model(obj_instance),
                               'object_id': obj_instance.pk})
        content = Content.objects.create(**content_kwargs)
        for tag in tags:
            content.tags.add(tag)
            content.save()

        return obj_instance


class ContentDelegateBase(models.Model):
    """
    Mixin for objects that'd like to be considered 'content.'
    """

    class Meta:
        abstract = True

    objects = ContentDelegateManager()

    @staticmethod
    def get_content_url(content):
        return None

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    @property
    def content(self):
        """
        Return the corresponding `base.models.Content` object.

        It should always exist, but if it doesn't, a `Content.DoesNotExist` exception will be raised.
        """
        # TODO cache this.
        return Content.objects.get(object_id=self.pk,
                                   content_type=ContentType.objects.get_for_model(self).id)
