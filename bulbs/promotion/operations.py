from django.db import models

from polymorphic import PolymorphicModel


class ContentListOperation(PolymorphicModel):

    class Meta:
        ordering = ["-when"]

    content_list = models.ForeignKey("promotion.ContentList", related_name="operations")
    when = models.DateTimeField()
    applied = models.BooleanField(default=False)

    def apply(self, data):
        raise NotImplemented()


class InsertOperation(ContentListOperation):

    index = models.IntegerField(default=0)
    content = models.ForeignKey("content.Content", related_name="+")
    lock = models.BooleanField(default=False)
    
    def apply(self, data):
        next = {
            "id": self.content.pk,
            "lock": self.lock
        }
        for i in range(self.index, min(len(data), 100)):
            if data[i].get("lock", False):
                continue
            next, data[i] = data[i], next  # Swap them
        data.append(next)
        return data


class ReplaceOperation(ContentListOperation):

    content = models.ForeignKey("content.Content", related_name="+")
    target = models.ForeignKey("content.Content", related_name="+")
    lock = models.BooleanField(default=False)

    def apply(self, data):
        replace = {
            "id": self.content.pk,
            "lock": self.lock
        }
        for index, item in enumerate(data):
            if item["id"] == self.target.pk:
                if item.get("lock", False):
                    raise Exception("That item is locked!")
                data[index] = replace
                break
        else:
            raise Exception("No content in list!")
        return data


class LockOperation(ContentListOperation):

    target = models.ForeignKey("content.Content", related_name="+")

    def apply(self, data):
        for index, item in enumerate(data):
            if item["id"] == self.target.pk:
                data[index]["lock"] = True
                break
        else:
            raise Exception("No content in list!")
        return data


class UnlockOperation(ContentListOperation):

    target = models.ForeignKey("content.Content", related_name="+")

    def apply(self, data):
        for index, item in enumerate(data):
            if item["id"] == self.target.pk:
                data[index]["lock"] = False
                break
        else:
            raise Exception("No content in list!")
        return data
