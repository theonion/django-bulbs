import logging

from django.db import models

from polymorphic import PolymorphicModel


logger = logging.getLogger(__name__)


class PZoneOperation(PolymorphicModel):

    pzone = models.ForeignKey("promotion.PZone", related_name="operations")
    when = models.DateTimeField()
    applied = models.BooleanField(default=False)
    content = models.ForeignKey("content.Content", related_name="+")

    def apply(self, data):
        raise NotImplemented()

    class Meta:
        ordering = ["when", "id"]


class InsertOperation(PZoneOperation):

    index = models.IntegerField(default=0)

    def apply(self, data):

        if self.content.published and self.when >= self.content.published:
            # content has a published date, and that date is before when this

            filtered = list(filter(lambda content: content["id"] == self.content.pk, data))
            if len(filtered) == 0:
                # content doesn't already exist in list
                data.insert(self.index, {
                    "id": self.content.pk
                })
                data = data[:100]
            else:
                # content already in list, don't insert, log a warning
                logger.warning(
                    "Failed to perform insert operation because content (id: %i) %s is already in %s!",
                    self.content.pk,
                    self.content.title,
                    self.pzone.name)

        else:
            # warn that we failed to perform an operation on this content
            logger.warning(
                "Failed to perform insert operation on unpublished content (id: %i) %s in %s!",
                self.content.pk,
                self.content.title,
                self.pzone.name)

        return data


class ReplaceOperation(PZoneOperation):

    index = models.IntegerField(default=0)

    def apply(self, data):

        if self.content.published and self.when >= self.content.published:
            # content has a published date, and that date is before when this
            #   operation is occurring
            try:
                filtered = list(filter(lambda content: content["id"] == self.content.pk, data))
                if len(filtered) == 0:
                    # content doesn't already exist in list
                    data[self.index] = {
                        "id": self.content.pk
                    }
                else:
                    # content already in list, don't insert, log a warning
                    logger.warning(
                        "Failed to perform replace operation because content (id: %i) %s is already in %s!",
                        self.content.pk,
                        self.content.title,
                        self.pzone.name)
            except IndexError:
                logger.warning(
                    "Failed to perform replace operation on content (id: %i) %s in %s at index %i!",
                    self.content.pk,
                    self.content.title,
                    self.pzone.name,
                    self.index)
        else:
            # warn that we failed to perform an operation on this content
            logger.warning(
                "Failed to perform replace operation on unpublished content (id: %i) %s in %s!",
                self.content.pk,
                self.content.title,
                self.pzone.name)

        return data


class DeleteOperation(PZoneOperation):
    """Delete a piece of content from the list, assumes only one instance of a
    piece of content is in the list."""

    def apply(self, data):
        for index, item in enumerate(data):
            if item["id"] == self.content.pk:
                del(data[index])
                break
        else:
            logger.warning(
                "Failed to perform delete operation on content (id: %i) %s in %s!",
                self.content.pk,
                self.content.title,
                self.pzone.name)
        return data
