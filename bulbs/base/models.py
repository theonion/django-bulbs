from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Tag(models.Model):
    tag = models.CharField(max_length=255)


class Content(models.Model):
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

