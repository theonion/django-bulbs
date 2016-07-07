from datetime import timedelta

from django.utils import timezone

from bulbs.super_features.models import BaseSuperFeature, GUIDE_TO
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureModelTestCase(BaseIndexableTestCase):

    def test_superfeature_creation(self):
        sf = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            published=timezone.now() + timedelta(weeks=1),
            superfeature_type=GUIDE_TO,
            tunic_campaign_id=1
        )
        db_sf = BaseSuperFeature.objects.get(pk=sf.pk)

        self.assertEqual(db_sf.pk, sf.pk)
