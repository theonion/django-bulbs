from django.db import models

from djes.models import IndexableManager


class SectionIndexableManager(IndexableManager):

    def get_by_identifier(self, identifier):
        identifier_id = identifier.split(".")[-1]
        return self.get(id=identifier_id)


class SectionManager(models.Manager):

    def get_by_identifier(self, identifier):
        identifier_id = identifier.split(".")[-1]
        return self.get(id=identifier_id)
