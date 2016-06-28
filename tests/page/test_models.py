from datetime import timedelta

from django.utils import timezone

from bulbs.page.models import Page, Status, TemplateType
from bulbs.utils.test import BaseIndexableTestCase


class PageModelTestCase(BaseIndexableTestCase):

    def test_page_creation(self):
        page = Page.objects.create(
            name="Guide to Cats",
            notes="This is the guide to cats",
            status=Status.DRAFT,
            publish_date=timezone.now() + timedelta(weeks=1),
            template_type=TemplateType.GUIDE_TO,
            tunic_campaign_id=1
        )
        db_page = Page.objects.get(pk=page.pk)

        self.assertEqual(db_page.pk, page.pk)
        self.assertEqual(page.slug, 'guide-to-cats')
