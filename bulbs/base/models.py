from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Tag(models.Model):
    tag = models.CharField(max_length=255)


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


    def __unicode__(self):
        return self.title


    class Meta:
        unique_together = (('content_type', 'object_id'),)
        verbose_name_plural = "content"


class ContentMixin(object):
    """
    Mixin for objects that'd like to be considered 'content.'
    """

    @property
    def content(self):
        """
        Return the corresponding `base.models.Content` object.
        """
        return Content.objects.get(object_id=self.pk,
                                   content_type=ContentType.objects.get_for_model(self).id)
