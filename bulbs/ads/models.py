from django.db import models
from json_field import JSONField


class TargetingOverride(models.Model):
    url = models.URLField(primary_key=True)
    targeting = JSONField()
