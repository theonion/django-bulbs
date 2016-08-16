from bulbs.utils.test import BaseIndexableTestCase
from bulbs.super_features.data_serializers import GuideToParentSerializer, GuideToChildSerializer
from bulbs.super_features.models import GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
from bulbs.super_features.registry import registry


class BaseSuperFeatureRegistryTestCase(BaseIndexableTestCase):

    def test_registry_stored(self):
        self.assertEqual(registry.registry, {
            GUIDE_TO_HOMEPAGE: (
                'Guide To Homepage',
                GuideToParentSerializer
            ),
            GUIDE_TO_ENTRY: (
                'Guide To Entry',
                GuideToChildSerializer
            )
        })

    def test_choices(self):
        self.assertEqual(registry.choices(), (
            (GUIDE_TO_HOMEPAGE, 'Guide To Homepage'),
            (GUIDE_TO_ENTRY, 'Guide To Entry')
        ))

    def test_serializers(self):
        self.assertEqual(registry.serializers(), {
            GUIDE_TO_HOMEPAGE: GuideToParentSerializer,
            GUIDE_TO_ENTRY: GuideToChildSerializer
        })
