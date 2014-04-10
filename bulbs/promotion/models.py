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
        return self.length

    def __iter__(self):
        content_ids = [item["id"] for item in self.data[:self.length]]
        bulk = Content.objects.in_bulk(content_ids)
        for pk in content_ids:
            yield bulk.get(pk)

    def __getitem__(self, index):
        if index >= self.length:
            raise IndexError("Index out of range")
        return Content.objects.get(id=self.data[index]["id"])

    def __setitem__(self, index, value):
        if index >= self.length:
            raise IndexError("Index out of range")
        if isinstance(value, Content):
            self.data[index]["id"] = value.pk
        elif isinstance(value, int):
            self.data[index]["id"] = value
        else:
            raise ValueError("ContentList items must be Content or int")

    def __delitem__(self, index):
        if index >= self.length:
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

    # @property
    # def content(self):
    #     content_ids = [item["id"] for item in self.data[:self.length]]
    #     bulk = Content.objects.in_bulk(content_ids)
    #     return [bulk.get(pk) for pk in content_ids]

    # @content.setter
    # def content(self, value):
    #     data = []
    #     for obj in value:
    #         if isinstance(obj, Content):
    #             data.append({"id": obj.pk})
    #         else:
    #             data.append({"id": obj})
    #     self.data = data


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    data = JSONField(default=[])
    date = models.DateTimeField(auto_now_add=True)
