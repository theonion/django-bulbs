from django.utils import timezone

from bulbs.campaigns.models import Campaign
from bulbs.content.models import Content
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class ContentManagerTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(ContentManagerTestCase, self).setUp()
        campaign = Campaign.objects.create(
            sponsor_name="TheCobbler",
            start_date=timezone.now() - timezone.timedelta(days=5),
            end_date=timezone.now() + timezone.timedelta(days=5)
        )
        make_content(evergreen=True, published=timezone.now(), _quantity=50)
        make_content(TestContentObj, campaign=campaign, published=timezone.now(), _quantity=50)
        Content.search_objects.refresh()

    def test_sponsored(self):
        sponsored = Content.search_objects.sponsored().extra(from_=0, size=50)
        qs = TestContentObj.objects.filter(campaign__isnull=False)
        self.assertEqual(qs.count(), sponsored.count())
        self.assertEqual(
            sorted([obj.id for obj in qs]),
            sorted([obj.id for obj in sponsored])
        )

    def test_evergreen(self):
        evergreen = Content.search_objects.evergreen().extra(from_=0, size=50)
        qs = TestContentObj.objects.filter(evergreen=True)
        self.assertEqual(qs.count(), evergreen.count())
        self.assertEqual(
            sorted([obj.id for obj in qs]),
            sorted([obj.id for obj in evergreen])
        )
