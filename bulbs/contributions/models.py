from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

from elasticsearch_dsl import field
from djes.models import Indexable, IndexableManager

from bulbs.content.models import Content, FeatureType


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


def calculate_hourly_pay(rate, minutes_worked):
    return ((float(rate) / 60) * minutes_worked)


class SlugObjectField(field.Object):

    def __init__(self, *args, **kwargs):
        super(SlugObjectField, self).__init__(*args, **kwargs)
        self.properties['slug'] = field.construct_field('string', index='not_analyzed')


class ContentField(field.Object):

    def __init__(self, *args, **kwargs):
        super(ContentField, self).__init__(*args, **kwargs)
        self.properties['slug'] = field.construct_field('string', not_analyzed=True)
        self.properties['feature_type'] = SlugObjectField(not_analyzed=True)
        self.properties['tags'] = field.construct_field({
            'type': 'nested',
            'properties': {
                'slug': {'type': 'string', 'index': 'not_analyzed'}
            }
        })

    def to_es(self, obj):
        doc = {
            'id': obj.id,
            'title': obj.title,
            'published': obj.published,
            'feature_type': obj.feature_type.to_dict() if obj.feature_type else {}
        }

        return doc

    def to_python(self, data):
        return Content.objects.get(id=data['id'])


class ContributorField(field.Object):

    def __init__(self, *args, **kwargs):
        super(ContributorField, self).__init__(*args, **kwargs)
        self.properties['id'] = field.Long()
        self.properties['username'] = field.String(index='not_analyzed')
        self.properties['payroll_name'] = field.String(index='not_analyzed')
        self.properties['is_freelance'] = field.Boolean()

    def to_es(self, obj):
        data = {
            'id': obj.id,
            'username': obj.username
        }
        profile = getattr(obj, 'freelanceprofile', None)
        if profile:
            data['is_freelance'] = profile.is_freelance
            data['payroll_name'] = getattr(profile, 'payroll_name', '')
        return data

    def to_python(self, data):
        user_cls = get_user_model()
        user = user_cls.objects.filter(id=data['id'])
        if user.exists():
            return user.first()


class ContributionField(field.Object):

    def __init__(self, *args, **kwargs):
        super(ContributionField, self).__init__(*args, **kwargs)
        self.properties['id'] = field.Long()
        self.properties['contributor'] = ContributorField()

    def to_es(self, obj):
        if issubclass(obj.__class__, models.Manager):
            data = []
            for instance in obj.all():
                obj_data = {}
                for prop in self.properties:
                    c_field = self.properties[prop]
                    ref = getattr(instance, prop)
                    if hasattr(c_field, 'to_es'):
                        obj_data[prop] = c_field.to_es(ref)
                    elif hasattr(ref, 'to_dict'):
                        obj_data[prop] = ref.to_dict()
                    else:
                        obj_data[prop] = ref
                data.append(obj_data)
        else:
            data = {}
            for prop in self.properties:
                c_field = self.properties[prop]
                ref = getattr(obj, prop)
                if hasattr(c_field, 'to_es'):
                    data[prop] = c_field.to_es(ref)
                elif hasattr(ref, 'to_dict'):
                    data[prop] = ref.to_dict()
                else:
                    data[prop] = ref
        return data

    def to_python(self, data):
        return data


class ReportContent(Content):

    reference = models.Manager()

    class Meta:
        proxy = True

    class Mapping(Content.Mapping):

        # contributions = ContributionField()
        tags = field.Nested()

        class Meta:
            orphaned = True
            includes = ('tags',)
            # excludes = ('contributions',)


class LineItem(models.Model):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.FloatField(default=0)
    note = models.TextField()
    payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-payment_date",)


class ContributorRole(Indexable):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    payment_type = models.IntegerField(choices=ROLE_PAYMENT_TYPES, default=MANUAL)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        created = bool(self.pk is None)
        super(ContributorRole, self).save(*args, **kwargs)
        self.create_feature_type_rates(created)

    def create_feature_type_rates(self, created=False):
        """
        If the role is being created we want to populate a rate for all existing feature_types.
        """
        if created:
            for feature_type in FeatureType.objects.all():
                FeatureTypeRate.objects.create(role=self, feature_type=feature_type, rate=0)

    def get_rate(self):
        if self.payment_type == FLAT_RATE:
            qs = self.flat_rates.all()
            if qs.exists():
                return qs.first()
        if self.payment_type == HOURLY:
            qs = self.hourly_rates.all()
            if qs.exists():
                return qs.first()
        return None


class Contribution(Indexable):
    role = models.ForeignKey(ContributorRole)
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="contributions")
    content = models.ForeignKey(Content, related_name="contributions")
    notes = models.TextField(null=True, blank=True)
    minutes_worked = models.IntegerField(null=True)
    force_payment = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    search_objects = IndexableManager()

    class Mapping:

        content = ContentField()
        contributor = ContributorField()
        pay = field.Long()

        class Meta:
            dynamic = False
            excludes = ('content', 'contributor')

    @property
    def pay(self):
        return self.get_pay

    @property
    def get_pay(self):
        return self._get_pay()

    @property
    def get_override(self):
        return self._get_override()

    def delete(self):
        self.delete_index()
        return super(Contribution, self).delete()

    def get_rate(self):
        payment_type = self.role.payment_type
        if payment_type == MANUAL:
            return self.manual_rates.all().first()

        if payment_type == FLAT_RATE:
            return self.role.flat_rates.filter().first()

        if self.content.feature_type and payment_type == FEATURETYPE:
            return self.content.feature_type.feature_type_rates.filter(
                role=self.role
            ).first()

        if payment_type == HOURLY:
            return self.role.hourly_rates.filter().first()

    def _get_override(self):
        # Get contribution specific overrides first.
        if self.role.payment_type in [0, 1] and self.override_contribution.exists():
            return self.override_contribution.first().rate

        override_profile = self.contributor.overrides.filter(role=self.role).first()
        if not override_profile:
            return None

        elif self.role.payment_type == 0 and override_profile.override_flatrate.exists():
            return override_profile.override_flatrate.first().rate

        elif (self.role.payment_type == 1):
            override = override_profile.override_feature_type.filter(
                feature_type=self.content.feature_type
            ).first()
            if override:
                return override.rate

        elif self.role.payment_type == 2 and override_profile.override_hourly.exists():
            minutes_worked = float(getattr(self, 'minutes_worked', 0))
            return calculate_hourly_pay(
                override_profile.override_hourly.first().rate, minutes_worked
            )

    def _get_pay(self):
        override = self.get_override
        if override:
            return override
        rate = self.get_rate()
        if isinstance(rate, HourlyRate):
            minutes_worked = getattr(self, 'minutes_worked', 0)
            if minutes_worked is None:
                minutes_worked = 0
            return calculate_hourly_pay(rate.rate, float(minutes_worked))
        if rate:
            return rate.rate
        return None


class OverrideProfile(Indexable):
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='overrides')
    role = models.ForeignKey(ContributorRole, related_name='overrides')

    class Meta:
        unique_together = (('contributor', 'role'),)


class BaseOverride(Indexable):
    rate = models.IntegerField(default=0)
    updated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-updated_on',)


class FeatureTypeOverride(BaseOverride):
    profile = models.ForeignKey(OverrideProfile, related_name='override_feature_type')
    feature_type = models.ForeignKey(FeatureType)


class FlatRateOverride(BaseOverride):
    profile = models.ForeignKey(OverrideProfile, related_name='override_flatrate')


class HourlyOverride(BaseOverride):
    profile = models.ForeignKey(OverrideProfile, related_name='override_hourly')


class ContributionOverride(BaseOverride):
    contribution = models.ForeignKey(Contribution, related_name='override_contribution')

    class Mapping:
        contribution = ContributionField()


class Rate(Indexable):
    name = models.IntegerField(choices=RATE_PAYMENT_TYPES, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    rate = models.IntegerField()

    class Meta:
        ordering = ('-updated_on',)


class FlatRate(Rate):
    role = models.ForeignKey(ContributorRole, related_name="flat_rates")


class HourlyRate(Rate):
    role = models.ForeignKey(ContributorRole, related_name="hourly_rates")


class ManualRate(Rate):
    contribution = models.ForeignKey(Contribution, related_name="manual_rates")

    class Mapping:
        contribution = ContributionField()


class FeatureTypeRate(Rate):
    role = models.ForeignKey(ContributorRole, null=True, related_name="feature_type_rates")
    feature_type = models.ForeignKey(FeatureType, related_name="feature_type_rates")

    class Meta:
        unique_together = (("role", "feature_type"))
        ordering = ("feature_type__name",)

    @property
    def feature_type_slug(self):
        return getattr(self.feature_type, "slug", None)


class FreelanceProfile(Indexable):
    payroll_name = models.CharField(max_length=256, blank=True, null=True)
    contributor = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True)
    is_freelance = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    def get_pay(self, start=None, end=None):
        qs = self.contributor.contributions.all()
        if start:
            qs = qs.filter(payment_date__gte=start)
        if end:
            qs = qs.filter(payment_date__lte=end)

        pay = 0
        for contribution in qs.all():
            contribution_pay = contribution.get_pay
            if contribution_pay:
                pay += contribution_pay
        return pay
