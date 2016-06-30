from datetime import timedelta

from django.utils import timezone

from bulbs.super_features.models import SuperFeature, Status, TemplateType
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureModelTestCase(BaseIndexableTestCase):

    def test_page_creation(self):
        sf = SuperFeature.objects.create(
            name="Guide to Cats",
            notes="This is the guide to cats",
            status=Status.DRAFT,
            publish_date=timezone.now() + timedelta(weeks=1),
            template_type=TemplateType.GUIDE_TO,
            tunic_campaign_id=1
        )
        db_sf = SuperFeature.objects.get(pk=sf.pk)

        self.assertEqual(db_sf.pk, sf.pk)
        self.assertEqual(sf.slug, 'guide-to-cats')
