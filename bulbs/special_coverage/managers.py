from django.db import models


class SpecialCoverageManager(models.Manager):
    def get_by_identifier(self, identifier):
        identifier_id = identifier.split(".")[-1]
        return super(SpecialCoverageManager, self).get_queryset().get(id=identifier_id)
