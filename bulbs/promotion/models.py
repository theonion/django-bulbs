from celery.task import task

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from json_field import JSONField

from bulbs.content.models import Content
from .operations import *  # noqa


@task
def update_pzone(**kwargs):
    """Update pzone data in the DB"""

    pzone = PZone.objects.get(**kwargs)

    # get the data and loop through operate_on, applying them if necessary
    when = timezone.now()
    data = pzone.data
    for operation in pzone.operations.filter(when__lte=when, applied=False):
        data = operation.apply(data)
        operation.applied = True
        operation.save()
    pzone.data = data

    # create a history entry
    pzone.history.create(data=pzone.data)

    # save modified pzone, making transactions permanent
    pzone.save()


class PZoneManager(models.Manager):

    def operate_on(self, when=None, apply=False, **kwargs):
        """Do something with operate_on. If apply is True, all transactions will
        be applied and saved via celery task."""

        # get pzone based on id
        pzone = self.get(**kwargs)

        # cache the current time
        now = timezone.now()

        # ensure we have some value for when
        if when is None:
            when = now

        if when < now:
            histories = pzone.history.filter(date__lte=when)
            if histories.exists():
                # we have some history, use its data
                pzone.data = histories[0].data

        else:
            # only apply operations if cache is expired or empty, or we're looking at the future
            data = pzone.data

            # Get the cached time of the next expiration
            next_operation_time = cache.get('pzone-operation-expiry-' + pzone.name)
            if next_operation_time is None or next_operation_time < when:

                # start applying operations
                pending_operations = pzone.operations.filter(when__lte=when, applied=False)
                for operation in pending_operations:
                    data = operation.apply(data)

                # reassign data
                pzone.data = data

                if apply and pending_operations.exists():
                    # there are operations to apply, do celery task
                    update_pzone.delay(**kwargs)

        # return pzone, modified if apply was True
        return pzone

    def preview(self, when=timezone.now(), **kwargs):
        """Preview transactions, but don't actually save changes to list."""

        return self.operate_on(when=when, apply=False, **kwargs)

    def applied(self, **kwargs):
        """Apply transactions via a background task, return preview to user."""

        return self.operate_on(apply=True, **kwargs)


class PZone(models.Model):
    name = models.SlugField(unique=True)
    zone_length = models.IntegerField(default=10)
    data = JSONField(default=[], blank=True)

    objects = PZoneManager()

    def __len__(self):
        return min(self.zone_length, len(self.data))

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
            raise ValueError("PZone items must be Content or int")

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

    def clean(self, *args, **kwargs):
        super(PZone, self).clean(*args, **kwargs)

        if not isinstance(self.data, list):
            raise ValidationError('PZone data must be formatted as a list')

        for instance in self.data:
            if not isinstance(instance, dict) or 'id' not in instance:
                raise ValidationError(
                    'PZone data objects must be formatted like the following "{id: int}"'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super(PZone, self).save(*args, **kwargs)


    class Meta:
        ordering = ["name"]


class PZoneHistory(models.Model):
    pzone = models.ForeignKey(PZone, related_name="history")
    data = JSONField(default=[])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # we want the most recently created to come out first
        ordering = ["-date"]
