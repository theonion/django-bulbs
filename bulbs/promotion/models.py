from django.db import models

from bulbs.content.models import Content


class ContentList(models.Model):
    name = models.SlugField()
    default_length = models.IntegerField(null=True, blank=True)
    content_ids = models.CommaSeparatedIntegerField(max_length=1000)

    @property
    def content(self):
        content_ids = [int(pk) for pk in self.content_ids.split(",")]
        bulk = Content.objects.in_bulk(content_ids)
        return [bulk.get(pk) for pk in content_ids]

    @content.setter
    def content(self, value):
        content_ids = []
        for obj in value:
            if isinstance(obj, Content):
                content_ids.append(str(obj.pk))
            else:
                content_ids.append(str(obj))
        self.content_ids = ",".join(content_ids)


class ContentListHistory(models.Model):
    content_list = models.ForeignKey(ContentList, related_name="history")
    content = models.CommaSeparatedIntegerField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
