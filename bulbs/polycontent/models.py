from django.db import models
from polymorphic import PolymorphicModel


class Content(PolymorphicModel):
    """
    This is the base content model from which all content derives.
    """
    time_published = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.title

