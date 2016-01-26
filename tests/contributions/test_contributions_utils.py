from django.contrib.auth import get_user_model

from bulbs.content.models import Content, FeatureType
from bulbs.contributions.models import (
    Contribution, ContributorRole, FeatureTypeRate, FeatureTypeOverride, FlatRate,
    FlatRateOverride, HourlyRate, HourlyOverride, OverrideProfile
)
from bulbs.contributions.utils import merge_roles
from bulbs.utils.test import BaseIndexableTestCase


class MergeRoleTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(MergeRoleTestCase, self).setUp()
        user_cls = get_user_model()
        self.dominant = ContributorRole.objects.create(name="Dominator")
        self.deprecated = ContributorRole.objects.create(name="Deprecated")
        self.fella = user_cls.objects.create(first_name="fella", last_name="guy")

        self.feature_types = [
            FeatureType.objects.create(name="surf"),
            FeatureType.objects.create(name="turf"),
            FeatureType.objects.create(name="smurf"),
            FeatureType.objects.create(name="burf")
        ]

        for i in range(100):
            content = Content.objects.create(title="a{}".format(i))
            if i % 2 == 0:
                content.contributions.create(role=self.dominant, contributor=self.fella)
            else:
                content.contributions.create(role=self.deprecated, contributor=self.fella)

        profile = OverrideProfile.objects.create(contributor=self.fella, role=self.deprecated)
        FlatRate.objects.create(role=self.deprecated, rate=40)
        FlatRateOverride.objects.create(profile=profile, rate=100)
        HourlyRate.objects.create(role=self.deprecated, rate=6)
        HourlyOverride.objects.create(profile=profile, rate=42)
        for feature_type in self.feature_types:
            FeatureTypeRate.objects.create(
                role=self.deprecated, rate=21, feature_type=feature_type
            )
            FeatureTypeOverride.objects.create(
                profile=profile, feature_type=feature_type
            )

    def test_contributions_merge(self):
        merge_roles(self.dominant.name, self.deprecated.name)
        for contribution in Contribution.objects.all():
            self.assertNotEqual(contribution.role, self.deprecated)

    def test_flat_rate_merge(self):
        self.assertFalse(self.dominant.flat_rates.exists())
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertTrue(self.dominant.flat_rates.exists())

    def test_flat_rate_merge_rate_exists(self):
        rate = FlatRate.objects.create(role=self.dominant, rate=20)
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertEqual(self.dominant.flat_rates.first().id, rate.id)
        self.assertEqual(self.dominant.flat_rates.count(), 1)

    def test_hourly_rate_merge(self):
        self.assertFalse(self.dominant.hourly_rates.exists())
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertTrue(self.dominant.hourly_rates.exists())

    def test_hourly_rate_merge_rate_exists(self):
        rate = HourlyRate.objects.create(role=self.dominant, rate=3)
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertEqual(self.dominant.hourly_rates.first().id, rate.id)
        self.assertEqual(self.dominant.hourly_rates.count(), 1)

    def test_feature_type_rate_merge(self):
        self.assertFalse(self.dominant.feature_type_rates.exists())
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertEqual(self.dominant.feature_type_rates.count(), len(self.feature_types))

    def test_feature_type_rate_merge_zero(self):
        for feature_type in self.feature_types:
            FeatureTypeRate.objects.create(rate=0, role=self.dominant, feature_type=feature_type)
        merge_roles(self.dominant.name, self.deprecated.name)
        for feature_type_rate in self.dominant.feature_type_rates.all():
            self.assertGreater(feature_type_rate.rate, 0)

    def test_feature_type_rate_merge_not_zero(self):
        for feature_type in self.feature_types:
            FeatureTypeRate.objects.create(rate=1, role=self.dominant, feature_type=feature_type)
        merge_roles(self.dominant.name, self.deprecated.name)
        for feature_type_rate in self.dominant.feature_type_rates.all():
            self.assertEqual(feature_type_rate.rate, 1)

    def test_override_merge(self):
        self.assertFalse(self.dominant.overrides.exists())
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertTrue(self.dominant.overrides.exists())

    def test_override_merge_exists_no_overrides(self):
        OverrideProfile.objects.create(role=self.dominant, contributor=self.fella)
        merge_roles(self.dominant.name, self.deprecated.name)
        self.assertEquals(
            self.dominant.overrides.first().override_feature_type.count(), len(self.feature_types)
        )
        self.assertTrue(self.dominant.overrides.first().override_flatrate.exists())
        self.assertTrue(self.dominant.overrides.first().override_hourly.exists())
