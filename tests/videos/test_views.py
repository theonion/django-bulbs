from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from bulbs.videos.models import VideohubVideo
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
