from django.conf import settings
from django.db import models

from bulbs.content.models import Content, FeatureType

# User = get_user_model()
# User = get_model(*settings.AUTH_USER_MODEL.split("."))

FLAT_RATE = 0
FEATURE_TYPE = 1
HOURLY = 2
MANUAL = 3
OVERRIDE = 4

ROLE_PAYMENT_TYPES = (
    (FLAT_RATE, 'Flat Rate'),
    (FEATURE_TYPE, 'Feature Type'),
    (HOURLY, 'Hourly'),
    (MANUAL, 'Manual')
)

RATE_PAYMENT_TYPES = ROLE_PAYMENT_TYPES + ((OVERRIDE, 'Override'),)


class ContributorRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    payment_type = models.CharField(choices=ROLE_PAYMENT_TYPES, default=MANUAL, max_length=255)


class Contribution(models.Model):
    role = models.ForeignKey(ContributorRole)
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.ForeignKey(Content)
    notes = models.TextField(null=True, blank=True)
    minutes_worked = models.IntegerField(null=True)


class Rate(models.Model):
    name = models.CharField(choices=RATE_PAYMENT_TYPES, default=MANUAL, max_length=255)
    updated_on = models.DateTimeField(auto_now=True)
    rate = models.IntegerField()

    class Meta:
        ordering = ('-updated_on',)


class ContributorRoleRate(Rate):
    role = models.ForeignKey(ContributorRole, related_name='rates')


class ContributionRate(Rate):
    contribution = models.ForeignKey(Contribution, related_name='rates')


class FeatureTypeRate(Rate):
    feature_type = models.ForeignKey(FeatureType, related_name='rates')
