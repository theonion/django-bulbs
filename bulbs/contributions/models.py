from bulbs.content.models import Content
from django.conf import settings
from django.db import models


# User = get_user_model()
# User = get_model(*settings.AUTH_USER_MODEL.split("."))


class ContributorRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)


class Contribution(models.Model):
    role = models.ForeignKey(ContributorRole)
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.ForeignKey(Content)
    notes = models.TextField(null=True, blank=True)
