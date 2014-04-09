from django.db import models
from django.utils import timezone

from json_field import JSONField

from bulbs.content.models import Content
from .operations import *  # noqa

class ContentListManager(models.Manager):
    
    def get(self, name, when=None, save=True):
        """Get the content list, including unapplied operations"""
        content_list = super(ContentListManager, self).get(name=name)
        if when is None:
            when = timezone.now()
        else:
            save = False  # As a safety feature, you can't save future states
        data = content_list.data
        for operation in content_list.operations.filter(when__lte=when, applied=False):
            data = operation.apply(data)
            if save:
                operation.applied = True

        content_list.data = data
        if save:
            content_list.save()

        return content_list


class ContentList(models.Model):
    name = models.SlugField(unique=True)
    length = models.IntegerField(null=True, blank=True)
    data = JSONField(default=[])

    objects = ContentListManager()

    @property
    def content(self):
        content_ids = [item["id"] for item in self.data[:self.length]]
        bulk = Content.objects.in_bulk(content_ids)
        return [bulk.get(pk) for pk in content_ids]

    @content.setter
    def content(self, value):
        data = []
        for obj in value:
            if isinstance(obj, Content):
                data.append({"id": obj.pk})
            else:
                data.append({"id": obj})
        self.data = data


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    data = JSONField(default=[])
    date = models.DateTimeField(auto_now_add=True)
