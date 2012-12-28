from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ContentManager(models.Manager):
    def tagged_as(self, *tag_names):
        """

        """
        if tag_names:
            return super(ContentManager, self).get_query_set().filter(tags__name__in=tag_names).distinct()
        else:
            return super(ContentManager, self).get_query_set()



class Content(models.Model):
    """
    Base Content object.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    tags = models.ManyToManyField(Tag)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = ContentManager()

    def __unicode__(self):
        return self.title


    class Meta:
        unique_together = (('content_type', 'object_id'),)
        verbose_name_plural = "content"


class ContentMixin(object):
    """
    Mixin for objects that'd like to be considered 'content.'
    """

    @classmethod
    def create_content(cls, **kwargs):
        """
        Create this object and the parent content object.
        """
        content_kwargs = {}
        obj_kwargs = {}

        for key, value in kwargs.iteritems():
            if key.startswith("content__"):
                new_key = "".join(key.split("content__")[1:])
                content_kwargs[new_key] = value
            else:
                obj_kwargs[key] = value

        # TODO wrap in transaction
        obj_instance = cls.objects.create(**obj_kwargs)

        content_kwargs.update({'content_type': ContentType.objects.get_for_model(obj_instance),
                               'object_id': obj_instance.pk})
        Content.objects.create(**content_kwargs)

        return obj_instance


    @property
    def content(self):
        """
        Return the corresponding `base.models.Content` object.
        """
        return Content.objects.get(object_id=self.pk,
                                   content_type=ContentType.objects.get_for_model(self).id)


class TestContentObj(models.Model, ContentMixin):
    field1 = models.CharField(max_length=255)
    field2 = models.CharField(max_length=255)
