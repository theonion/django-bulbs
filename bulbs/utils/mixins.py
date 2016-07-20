from django.db import models


class ParentOrderingMixin(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    ordering = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        abstract = True
