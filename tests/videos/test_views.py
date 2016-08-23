from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from bulbs.videos.models import VideohubVideo
from bulbs.videos.views import VideoRedirectView
from bulbs.utils.test import make_content

from example.testcontent.models import TestVideoContentObj


class RedirectViewTestCase(TestCase):

    def setUp(self):
        super(RedirectViewTestCase, self).setUp()
        self.videohub_video = VideohubVideo.objects.create(id=2)
        self.video = make_content(
            TestVideoContentObj, videohub_ref=self.videohub_video, published=timezone.now()
        )

    def test_redirect_success(self):
        url = reverse("video_redirect", kwargs={"videohub_ref_id": self.video.videohub_ref.pk})
        self.assertEqual(url, "/v/2")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.video.get_absolute_url(), resp['Location'])


class VideoRedirectViewTestCase(TestCase):

    def setUp(self):
        super(VideoRedirectViewTestCase, self).setUp()
        self.view = VideoRedirectView()
        self.videohub_video = VideohubVideo.objects.create(id=4382)
        self.older_video = make_content(
            TestVideoContentObj, videohub_ref=self.videohub_video, published=timezone.now()
        )
        self.newer_video = make_content(
            TestVideoContentObj, videohub_ref=self.videohub_video, published=timezone.now()
        )

    def test_choose_video_for_redirect_chooses_first_video(self):
        videos = [self.older_video, self.newer_video]
        self.assertEqual(self.view.choose_video_for_redirect(videos), self.older_video)

    def test_choose_for_redirect_chooses_none(self):
        videos = []
        self.assertEqual(self.view.choose_video_for_redirect(videos), None)

    def test_get_videos_for_redirect_gets_videos_for_videohub_ref_id(self):
        self.assertSequenceEqual(self.view.get_videos_for_redirect('4382'), [self.newer_video, self.older_video])

    def test_redirects_to_new_video(self):
        response = self.view.get(None, '4382')
        self.assertEqual(response['Location'], self.newer_video.get_absolute_url())

    def test_404_when_no_matching_video(self):
        with self.assertRaises(Http404):
            self.view.get(None, '83728372729')
