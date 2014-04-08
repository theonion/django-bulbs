from django.db import models

from bulbs.content.models import Content


class ContentList(models.Model):
    name = models.SlugField()
    default_length = models.IntegerField(null=True, blank=True)
    content_ids = models.CommaSeparatedIntegerField(max_length=1000)

    @property
    def content(self):
        bulk = Content.objects.in_bulk(self.content_ids)
        return [bulk.get(pk) for pk in self.content_ids]


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    content = models.CommaSeparatedIntegerField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
