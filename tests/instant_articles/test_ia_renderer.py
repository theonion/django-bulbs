from django.test.utils import override_settings

from bulbs.instant_articles.renderer import InstantArticleRenderer
from bulbs.utils.test import BaseIndexableTestCase


@override_settings(BETTY_IMAGE_URL='//images.onionstatic.com/onion')
class InstantArticleRendererTests(BaseIndexableTestCase):
    def setUp(self):
        super(InstantArticleRendererTests, self).setUp()
        self.renderer = InstantArticleRenderer()

    def test_render_betty(self):
        block = {"betty": {"image_id": 2349}}
        output = self.renderer.render_betty(block['betty'])

        self.assertEqual(
            output.replace('\n', ''),
            "<figure><img src=\"//images.onionstatic.com/onion/2349/16x9/1920.jpg\" /></figure>"
        )

    # def test_render_facebook(self):
    #     pass

    def test_render_instagram(self):
        block = {"instagram": {"instagram_id": "3ewOSHitL2"}}

        output = self.renderer.render_instagram(block['instagram'])
        self.assertTrue(
            output.replace('\n', ''),
            '<figure><iframe src="https://www.instagram.com/p/3ewOSHitL2/embed"></iframe></figure>'
        )

    # def test_render_twitter(self):
    #     pass
    #
    # def test_render_onion_video(self):
    #     pass
    #
    # def test_render_soundcloud(self):
    #     pass
    #
    # def test_render_vimeo(self):
    #     pass

    def test_render_youtube(self):
        block = {"youtube": {"video_id": "2vnd49"}}
        output = self.renderer.render_youtube(block["youtube"])

        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe width="560" height="315" src="https://www.youtube.com/embed/2vnd49" frameborder="0" allowfullscreen></iframe></figure>'
        )
