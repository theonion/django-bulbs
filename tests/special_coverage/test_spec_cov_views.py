from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone

from model_mommy import mommy

from bulbs.utils.test import BaseIndexableTestCase, make_content
from bulbs.campaigns.models import Campaign
from bulbs.special_coverage.models import SpecialCoverage

from example.testcontent.models import TestContentObj


class TestSpecialCoverageViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestSpecialCoverageViews, self).setUp()
        User = get_user_model()
        self.client = Client()

        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_special_coverage_view(self):
        campaign = Campaign.objects.create(
            sponsor_name="Campaign"
        )

        # create content for Special Coverage
        content = make_content(published=timezone.now())
        content.__class__.search_objects.refresh()

        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            active=True,
            query={
                "included_ids": [content.id]
            },
            videos=[],
            campaign=campaign,
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        sc.save()

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 200)

        import pdb; pdb.set_trace()
        # check that content_list is set

    def test_inactive_special_coverage_view(self):
        pass
