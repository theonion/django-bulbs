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
