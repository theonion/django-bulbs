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
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            "<figure><img src=\"//images.onionstatic.com/onion/2349/16x9/1920.jpg\" /><figcaption>A really good caption</figcaption></figure>"
        )

    def test_render_facebook(self):
        block = {"facebook": {"iframe": '<iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fsarahpalin%2Fposts%2F10154115152888588&width=500" width="500" height="603" scrolling="no" frameborder="0" allowTransparency="true"></iframe>'}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fsarahpalin%2Fposts%2F10154115152888588&width=500" width="500" height="603" scrolling="no" frameborder="0" allowTransparency="true"></iframe></figure>'
        )

    def test_render_imgur(self):
        block = {"imgur": {"iframe": '<iframe allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true" class="imgur-embed-iframe-pub imgur-embed-iframe-pub-a-K1DxV-true-540" scrolling="no" src="http://imgur.com/a/K1DxV/embed?pub=true&amp;ref=http%3A%2F%2Fstaff.avclub.com%2Fcms%2Fapp%2Fedit%2F236963%2F&amp;w=540" id="imgur-embed-iframe-pub-a-K1DxV"></iframe>'}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true" class="imgur-embed-iframe-pub imgur-embed-iframe-pub-a-K1DxV-true-540" scrolling="no" src="http://imgur.com/a/K1DxV/embed?pub=true&amp;ref=http%3A%2F%2Fstaff.avclub.com%2Fcms%2Fapp%2Fedit%2F236963%2F&amp;w=540" id="imgur-embed-iframe-pub-a-K1DxV"></iframe></figure>'
        )

    def test_render_instagram(self):
        block = {"instagram": {"instagram_id": "3ewOSHitL2"}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe class="instagram-media instagram-media-rendered" id="instagram-embed-0" src="https://www.instagram.com/p/3ewOSHitL2/embed/captioned/?v=7" allowtransparency="true" frameborder="0"></iframe></figure>'
        )

    def test_render_text(self):
        block = {"text": {"raw": "<p>This is a paragraph of text</p>"}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<p>This is a paragraph of text</p>'
        )

    def test_render_twitter(self):
        block = {"twitter": {"blockquote": '''
            <blockquote class="twitter-tweet" lang="en">
                 <p>To reduce my views to a handful of jokes that didn’t land is not a true reflection of my character, nor my evolution as a comedian.</p>
                 — Trevor Noah (@Trevornoah) <a href="https://twitter.com/Trevornoah/status/583019964556152832">March 31, 2015</a>
            </blockquote>
        '''}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
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

    def test_render_onion_video(self):
        block = {'onion_video': {'iframe': '<iframe src="http://onionstudios.com/embed?id=3040" class="onionstudios-playlist" allowfullscreen="" webkitallowfullscreen="" mozallowfullscreen="" frameborder="no" width="560" height="315" scrolling="no"></iframe>'}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe src="http://onionstudios.com/embed?id=3040" class="onionstudios-playlist" allowfullscreen="" webkitallowfullscreen="" mozallowfullscreen="" frameborder="no" width="560" height="315" scrolling="no"></iframe></figure>'
        )

    def test_render_soundcloud(self):
        block = {'soundcloud': {'iframe': '<iframe width="100%" height="450" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/playlists/119434855%3Fsecret_token%3Ds-Dv1kg&amp;color=ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false"></iframe>'}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe width="100%" height="450" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/playlists/119434855%3Fsecret_token%3Ds-Dv1kg&amp;color=ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false"></iframe></figure>'
        )

    def test_render_vimeo(self):
        block = {'vimeo': {'iframe': '<iframe src="https://player.vimeo.com/video/166544005" width="640" height="360" frameborder="0" webkitallowfullscreen="" mozallowfullscreen="" allowfullscreen=""></iframe>'}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe src="https://player.vimeo.com/video/166544005" width="640" height="360" frameborder="0" webkitallowfullscreen="" mozallowfullscreen="" allowfullscreen=""></iframe></figure>'
        )

    def test_render_youtube(self):
        block = {"youtube": {"video_id": "2vnd49"}}
        name, data = block.items()[0]

        output = self.renderer.render_item(name, data)
        self.assertEqual(
            output.replace('\n', ''),
            '<figure class="op-social"><iframe width="560" height="315" src="https://www.youtube.com/embed/2vnd49" frameborder="0" allowfullscreen></iframe></figure>'
        )
