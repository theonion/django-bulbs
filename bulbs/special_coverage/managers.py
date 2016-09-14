from django.db import models
from django.utils import timezone


class SpecialCoverageManager(models.Manager):
    def get_by_identifier(self, identifier):
        identifier_id = identifier.split(".")[-1]
        return super(SpecialCoverageManager, self).get_queryset().get(id=identifier_id)

    def active(self):
        qs = super(SpecialCoverageManager, self).get_queryset()
        now = timezone.now()

        return qs.filter(
            start_date__lte=now, end_date__gte=now
        ) | qs.filter(
            start_date__lte=now, end_date__isnull=True
        )

    def inactive(self):
        qs = super(SpecialCoverageManager, self).get_queryset()
        now = timezone.now()

        return qs.filter(start_date__lte=now, end_date__lte=now)
