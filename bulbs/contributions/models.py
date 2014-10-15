from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

from bulbs.content.models import Content


class ContributorRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)


class Contribution(models.Model):
    role = models.ForeignKey(ContributorRole)
    contributor = models.ForeignKey(User)
    content = models.ForeignKey(Content)
    notes = models.TextField(null=True, blank=True)
