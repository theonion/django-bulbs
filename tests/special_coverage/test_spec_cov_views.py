from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase, make_content
from bulbs.special_coverage.models import SpecialCoverage
from bulbs.videos.models import VideohubVideo
from mock import patch


class TestSpecialCoverageViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestSpecialCoverageViews, self).setUp()
        User = get_user_model()
        self.client = Client()

        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

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
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['special_coverage'], sc)
        self.assertEqual(response.context['content_list'].count(), sc.get_content().count())
        self.assertEqual(response.context['content_list'][0].id, content.id)
        self.assertEqual(response.context['video'], None)
        self.assertEqual(response.context['targeting'], {
            'dfp_specialcoverage': 'test-coverage',
        })
        self.assertEqual(
            response.template_name[0], 'special_coverage/custom/test_coverage_custom.html'
        )
        self.assertEqual(response.template_name[1], 'special_coverage/landing.html')

    def test_special_coverage_unpublished(self):
        content = make_content(published=timezone.now())
        unpublished_content = make_content(published=None)
        content.__class__.search_objects.refresh()

        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            query={
                "included_ids": [content.id, unpublished_content.id]
            },
            videos=[],
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['special_coverage'], sc)
        self.assertEqual(response.context['content_list'].count(), sc.get_content().count())
        self.assertEqual(response.context['content_list'][0].id, content.id)
        self.assertEqual(response.context['video'], None)
        self.assertEqual(response.context['targeting'], {
            'dfp_specialcoverage': 'test-coverage',
        })
        self.assertEqual(
            response.template_name[0], 'special_coverage/custom/test_coverage_custom.html'
        )
        self.assertEqual(response.template_name[1], 'special_coverage/landing.html')

        response = self.client.get(
            reverse("special", kwargs={"slug": sc.slug}) + "?full_preview=True"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['special_coverage'], sc)
        self.assertEqual(
            response.context['content_list'].count(), sc.get_content(published=False).count()
        )
        self.assertEqual(response.context['content_list'][0].id, content.id)
        self.assertEqual(response.context['content_list'][1].id, unpublished_content.id)


    def test_sets_first_video_to_video(self):
        content = make_content(published=timezone.now())
        content.__class__.search_objects.refresh()

        video = VideohubVideo.objects.create(id=4348)

        sc = SpecialCoverage.objects.create(
            name="Test Coverage",
            slug="test-coverage",
            description="Testing special coverage",
            query={
                "included_ids": [content.id]
            },
            videos=[4348, 3928],
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )
        with patch("bulbs.special_coverage.views.get_video_object_from_videohub_id") as mock_get_vid:
            mock_get_vid.return_value = video
            response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
            self.assertEqual(response.context['video'], video)

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
            start_date=timezone.now() - timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

        response = self.client.get(reverse("special", kwargs={"slug": sc.slug}))
        self.assertEqual(response.status_code, 404)
