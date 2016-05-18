# -*- coding: utf-8 -*-

from django.test.utils import override_settings

from bulbs.instant_articles.renderer import InstantArticleRenderer
from bulbs.utils.test import BaseIndexableTestCase


@override_settings(BETTY_IMAGE_URL='//images.onionstatic.com/onion')
class InstantArticleRendererTests(BaseIndexableTestCase):

    def setUp(self):
        super(InstantArticleRendererTests, self).setUp()
        self.renderer = InstantArticleRenderer()

    def test_render_betty(self):
        block = {"betty": {"image_id": 2349, "caption": "A really good caption"}}
        output = self.renderer.render_betty(block['betty'])

        self.assertEqual(
            output.replace('\n', ''),
            "<figure><img src=\"//images.onionstatic.com/onion/2349/16x9/1920.jpg\" /><figcaption>A really good caption</figcaption></figure>"
        )

    def test_render_facebook(self):
        block = {"facebook": {"iframe": '<iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fsarahpalin%2Fposts%2F10154115152888588&width=500" width="500" height="603" scrolling="no" frameborder="0" allowTransparency="true"></iframe>'}}
        output = self.renderer.render_facebook(block['facebook'])

        self.assertEqual(
            output.replace('\n', ''),
            '<figure><iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fsarahpalin%2Fposts%2F10154115152888588&width=500" width="500" height="603" scrolling="no" frameborder="0" allowTransparency="true"></iframe></figure>'
        )

    def test_render_instagram(self):
        block = {"instagram": {"instagram_id": "3ewOSHitL2"}}

        output = self.renderer.render_instagram(block['instagram'])
        self.assertTrue(
            output.replace('\n', ''),
            '<figure><iframe src="https://www.instagram.com/p/3ewOSHitL2/embed"></iframe></figure>'
        )

    def test_render_twitter(self):
        block = {"twitter": {"blockquote": '''
            <blockquote class="twitter-tweet" lang="en">
                 <p>To reduce my views to a handful of jokes that didn’t land is not a true reflection of my character, nor my evolution as a comedian.</p>
                 — Trevor Noah (@Trevornoah) <a href="https://twitter.com/Trevornoah/status/583019964556152832">March 31, 2015</a>
            </blockquote>
        '''}}

        output = self.renderer.render_twitter(block['twitter'])
        self.assertTrue(
            output.replace('\n', ''),
            '''
            <figure class="op-social">
                <iframe>
                    <blockquote class="twitter-tweet" lang="en">
                         <p>To reduce my views to a handful of jokes that didn’t land is not a true reflection of my character, nor my evolution as a comedian.</p>
                         — Trevor Noah (@Trevornoah) <a href="https://twitter.com/Trevornoah/status/583019964556152832">March 31, 2015</a>
                    </blockquote>
                    <script async="" src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
                </iframe>
            </figure>
            '''.replace('\n', '')
        )

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
