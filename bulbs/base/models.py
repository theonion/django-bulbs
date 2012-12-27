from django.contrib.contenttypes import generic
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import dispatcher

class Content(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

