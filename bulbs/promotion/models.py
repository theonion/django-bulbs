from django.db import models
from django.utils import timezone

from json_field import JSONField

from bulbs.content.models import Content
from .operations import *  # noqa


class ContentListManager(models.Manager):
    
    def preview(self, name, when):
        content_list = self.get(name=name)
        data = content_list.data
        for operation in content_list.operations.filter(when__lte=when, applied=False):
            data = operation.apply(data)

        content_list.data = data
        return content_list

    def applied(self, name):
        content_list = self.get(name=name)
        data = content_list.data
        for operation in content_list.operations.filter(when__lte=timezone.now(), applied=False):
            data = operation.apply(data)
            operation.applied = True

        content_list.data = data
        content_list.save()
        return content_list


class ContentList(models.Model):
    name = models.SlugField(unique=True)
    length = models.IntegerField(default=10)
    data = JSONField(default=[])

    objects = ContentListManager()

    def __len__(self):
        return min(self.length, len(self.data))

    def __iter__(self):
        content_ids = [item["id"] for item in self.data[:self.__len__()]]
        bulk = Content.objects.in_bulk(content_ids)
        for pk in content_ids:
            yield bulk.get(pk)

    def __getitem__(self, index):
        items = self.data[:self.__len__()].__getitem__(index)
        if isinstance(items, dict):
            return Content.objects.get(id=self.data[index]["id"])
        if isinstance(items, list):
            content = []
            content_ids = [item["id"] for item in items]
            bulk = Content.objects.in_bulk(content_ids)
            for pk in content_ids:
                content.append(bulk.get(pk))
            return content
        raise IndexError("Index out of range")

    def __setitem__(self, index, value):
        if index > self.__len__():
            raise IndexError("Index out of range")
        if isinstance(value, Content):
            self.data[index]["id"] = value.pk
        elif isinstance(value, int):
            self.data[index]["id"] = value
        else:
            raise ValueError("ContentList items must be Content or int")

    def __delitem__(self, index):
        if index > self.__len__():
            raise IndexError("Index out of range")
        del self.data[index]

    def __contains__(self, value):
        if isinstance(value, Content):
            value = value.pk
        if isinstance(value, int):
            for item in self.data:
                if value == item["id"]:
                    return True
        return False

    def __unicode__(self):
        return "{}[{}]".format(self.name, self.__len__())


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    data = JSONField(default=[])
    date = models.DateTimeField(auto_now_add=True)
