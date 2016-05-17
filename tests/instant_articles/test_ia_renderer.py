from bulbs.instant_articles.renderer import InstantArticleRenderer
from bulbs.utils.test import BaseIndexableTestCase


class InstantArticleRendererTests(BaseIndexableTestCase):
    def setUp(self):
        super(InstantArticleRendererTests, self).setUp()
        self.renderer = InstantArticleRenderer([])

    def test_render_betty(self):
        block = {"betty": {"image_id": 2349}}
        output = self.renderer.render_betty(block['betty'])

        self.assertEqual(output.replace('\n', ''), "<figure><img src=\"images/2349/16x9/1920.jpg\" /></figure>")

    # def test_render_facebook(self):
    #     pass
    #
    # def test_render_instagram(self):
    #     block = {"instagram": {"iframe": """
    #         <iframe>GET IFRAMEEXAMPLE</iframe>
    #     """}}
    #
    #     output = self.renderer.render_instagram(block)
    #     self.assertTrue(output)
    #     pass
    #
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
    #
    # def test_render_youtube(self):
    #     pass
