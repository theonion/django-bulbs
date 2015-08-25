from django.conf import settings
from django.db import models

from polymorphic import PolymorphicModel, PolymorphicManager

from bulbs.content.models import Content, FeatureType

# User = get_user_model()
# User = get_model(*settings.AUTH_USER_MODEL.split("."))

FLAT_RATE = 0
FEATURETYPE = 1
HOURLY = 2
MANUAL = 3
OVERRIDE = 4

ROLE_PAYMENT_TYPES = (
    (FLAT_RATE, 'Flat Rate'),
    (FEATURETYPE, 'FeatureType'),
    (HOURLY, 'Hourly'),
    (MANUAL, 'Manual')
)

RATE_PAYMENT_TYPES = ROLE_PAYMENT_TYPES + ((OVERRIDE, 'Override'),)


class LineItem(models.Model):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.IntegerField(default=0)
    note = models.TextField()
    payment_date = models.DateTimeField(auto_now_add=True)


class ContributorRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    payment_type = models.IntegerField(choices=ROLE_PAYMENT_TYPES, default=MANUAL)


class Contribution(models.Model):
    role = models.ForeignKey(ContributorRole)
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.ForeignKey(Content)
    notes = models.TextField(null=True, blank=True)
    minutes_worked = models.IntegerField(null=True)

    def get_rate(self):
        if self.rates.filter(name=OVERRIDE).count() > 0:
            return self.rates.filter(name=OVERRIDE).first()

        payment_type = self.role.payment_type
        if payment_type == MANUAL:
            return self.rates.all().first()

        if payment_type == FLAT_RATE:
            return self.role.rates.filter(name=payment_type).first()

        if payment_type == FEATURETYPE:
            return self.content.feature_type.rates.all().first()

        if payment_type == HOURLY:
            return self.role.rates.filter(name=payment_type).first()


class Rate(models.Model):
    name = models.IntegerField(choices=RATE_PAYMENT_TYPES, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    rate = models.IntegerField()

    class Meta:
        ordering = ('-updated_on',)


class ContributorRoleRate(Rate):
    role = models.ForeignKey(ContributorRole, related_name="rates")


class Override(PolymorphicModel, Rate):
    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="overrides"
    )
    role = models.ForeignKey(ContributorRole, related_name="overrides")

    objects = PolymorphicManager()


class FeatureTypeOverride(Override):
    """Overrides the rate for a user given a particular FeatureType."""
    feature_type = models.ForeignKey(FeatureType, related_name="overrides")


class ContributionRate(Rate):
    contribution = models.ForeignKey(Contribution, related_name="rates")


class FeatureTypeRate(Rate):
    feature_type = models.ForeignKey(FeatureType, related_name="rates")
