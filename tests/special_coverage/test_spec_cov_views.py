from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client, override_settings
from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase, make_content
from bulbs.campaigns.models import Campaign
from bulbs.special_coverage.models import SpecialCoverage


class TestSpecialCoverageViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestSpecialCoverageViews, self).setUp()
        User = get_user_model()
        self.client = Client()

        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

        self.campaign = Campaign.objects.create(
            sponsor_name="Campaign"
        )

    def test_special_coverage_view(self):
        content = make_content(published=timezone.now())
        content.__class__.search_objects.refresh()

        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            query={
                "included_ids": [content.id]
            },
            videos=[],
            campaign=self.campaign,
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['special_coverage'], sc)
        self.assertEqual(response.context['content_list'].count(), sc.get_content().count())
        self.assertEqual(response.context['content_list'][0].id, content.id)
        self.assertEqual(response.context['targeting'], {
            'dfp_specialcoverage': 'test-coverage',
            'dfp_campaign_id': self.campaign.id,
        })
        self.assertEqual(response.template_name[0], 'special_coverage/landing.html')

    def test_inactive_special_coverage_view(self):
        content = make_content(published=timezone.now())
        content.__class__.search_objects.refresh()

        # create old special coverage
        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            query={
                "included_ids": [content.id]
            },
            videos=[],
            campaign=self.campaign,
            start_date=timezone.now() - timezone.timedelta(days=20),
            end_date=timezone.now() - timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 404)

    def test_no_content_special_coverage_view(self):
        # create special coverage with no content
        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            query={},
            videos=[],
            campaign=self.campaign,
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 404)
