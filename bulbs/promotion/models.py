from django.db import models
from django.utils import timezone

from json_field import JSONField
from polymorphic import PolymorphicModel

from bulbs.content.models import Content


class ContentListManager(models.Manager):
    
    def get(self, when=None, save=True):
        """Get the content list, including unapplied operations"""


class ContentList(models.Model):
    name = models.SlugField(unique=True)
    default_length = models.IntegerField(null=True, blank=True)
    data = JSONField(default=[])

    @property
    def content(self):
        content_ids = [item["id"] for item in self.data]
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


class ContentListOperation(PolymorphicModel):

    class Meta:
        abstract = True

    content_list = models.ForeignKey(ContentList)
    when = models.DateTimeField()
    applied = models.BooleanField(default=False)

    def apply(self):
        raise NotImplemented()


class Insert(ContentListOperation):

    index = models.IntegerField(default=0)
    content = models.ForeignKey(Content)
    lock = models.BooleanField(default=False)
    
    def apply(self):
        cl = self.content_list.content
        cl.insert(self.index, self.content)
        self.content_list.content = cl


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    data = JSONField(default=[])
    date = models.DateTimeField(auto_now_add=True)
