from datetime import timedelta

from django.utils import timezone

from bulbs.page.models import SuperFeature, Status, TemplateType
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureModelTestCase(BaseIndexableTestCase):

    def test_page_creation(self):
        page = SuperFeature.objects.create(
            name="Guide to Cats",
            notes="This is the guide to cats",
            status=Status.DRAFT,
            publish_date=timezone.now() + timedelta(weeks=1),
            template_type=TemplateType.GUIDE_TO,
            tunic_campaign_id=1
        )
        db_page = SuperFeature.objects.get(pk=page.pk)

        self.assertEqual(db_page.pk, page.pk)
        self.assertEqual(page.slug, 'guide-to-cats')
