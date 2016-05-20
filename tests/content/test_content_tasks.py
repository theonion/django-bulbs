from bulbs.content.models import FeatureType
from bulbs.content.tasks import update_feature_type_rates
from bulbs.utils.test import BaseIndexableTestCase
from bulbs.contributions.models import ContributorRole, FeatureTypeRate


class FeatureTypeTasksTestCase(BaseIndexableTestCase):
    def test_update_feature_type_rates(self):
        role = ContributorRole.objects.create(name='Test Role', payment_type=1)
        feature_type = FeatureType.objects.create(
            name='Test Feature Type',
            slug='test-feature-type',
            instant_article=False)

        update_feature_type_rates(feature_type.pk)

        feature_type_rate = FeatureTypeRate.objects.order_by('id')[0]
        self.assertEqual(feature_type_rate.feature_type_id, feature_type.pk)
        self.assertEqual(feature_type_rate.role_id, role.pk)

    def test_existing_feature_type_rates(self):
        role = ContributorRole.objects.create(name='Test Role', payment_type=1)
        feature_type = FeatureType.objects.create(
            name='Existing Feature Type',
            slug='existing-feature-type',
            instant_article=False
        )

        self.assertEqual(FeatureTypeRate.objects.all().count(), 1)

        # Clean slate
        FeatureTypeRate.objects.all().delete()

        FeatureTypeRate.objects.create(
            rate=0,
            feature_type_id=feature_type.pk,
            role_id=role.pk
        )
        self.assertEqual(FeatureTypeRate.objects.all().count(), 1)

        feature_type.save()
        self.assertEqual(FeatureTypeRate.objects.all().count(), 1)
