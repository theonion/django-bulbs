# -*- coding: utf-8 -*-

import os.path
import unittest

from bs4 import BeautifulSoup

from bulbs.instant_articles.parser import (parse_betty,
                                           parse_body,
                                           parse_facebook,
                                           parse_imgur,
                                           parse_instagram,
                                           parse_onion_video,
                                           parse_soundcloud,
                                           parse_text,
                                           parse_twitter,
                                           parse_twitter_video,
                                           parse_vimeo,
                                           parse_youtube,
                                           )


def parse_raw_tag(html):
    return [c for c in BeautifulSoup(html.strip()).children][0]


def read_data(name):
    here = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(here, 'test_data', 'input', name + '.html')).read()


def read_tag_data(name):
    return parse_raw_tag(read_data(name))


class ParseBodyTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], parse_body(''))
        self.assertEqual([], parse_body('<div></div>'))

    def test_multiple(self):
        self.assertEqual([{'text': {'raw': '<p>First paragraph.</p>'}},
                          {'betty': {'image_id': '9513',
                                     'caption': u"Testing «ταБЬℓσ» we're 20% done!"}},
                          {'text': {'raw': '<p>Second <i>paragraph</i>.</p>'}},
                          {'text': {'raw': '<p>Third paragraph.</p>'}}],
                         parse_body(read_data('body-multiple')))


class ParseBettyTest(unittest.TestCase):

    def test_match(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u"Testing «ταБЬℓσ» we're 20% done!"}},
                         parse_betty(read_tag_data('betty-caption')))

    def test_missing_caption(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u''}},
                         parse_betty(read_tag_data('betty-no-caption')))


class ParseFacebookTest(unittest.TestCase):

    def test_post(self):
        tag = parse_raw_tag(parse_facebook(read_tag_data('facebook-post'))['facebook']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertTrue(tag['src'].startswith('https://www.facebook.com/plugins/post.php?'))
        self.assertFalse(tag.has_attr('style'))  # Verify removed

    def test_video(self):
        tag = parse_raw_tag(parse_facebook(read_tag_data('facebook-video'))['facebook']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertTrue(tag['src'].startswith('https://www.facebook.com/plugins/video.php?'))
        self.assertFalse(tag.has_attr('style'))  # Verify removed


class ParseImgurTest(unittest.TestCase):

    def test_parse(self):
        tag = parse_raw_tag(parse_imgur(read_tag_data('imgur'))['imgur']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertIn('imgur-embed-iframe-pub', tag['class'])


class ParseInstagramTest(unittest.TestCase):

    def test_iframe(self):
        self.assertEqual({'instagram': {'instagram_id': '3ewOSHitL2'}},
                         parse_instagram(read_tag_data('instagram-iframe')))

    def test_blockquote(self):
        self.assertEqual({'instagram': {'instagram_id': '3jeiuICtD7'}},
                         parse_instagram(read_tag_data('instagram-blockquote')))

    def test_instagram_div(self):
        self.assertEqual({'instagram': {'instagram_id': 'BE9ZB_3LVWa'}},
                         parse_instagram(read_tag_data('instagram-div')))


class ParseOnionVideoTest(unittest.TestCase):

    def test_parse(self):
        tag = parse_raw_tag(parse_onion_video(
            read_tag_data('onion_video'))['onion_video']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertEqual(['onionstudios-playlist'], tag['class'])


class ParseSoundcloudTest(unittest.TestCase):

    def test_parse(self):
        tag = parse_raw_tag(parse_soundcloud(read_tag_data('soundcloud'))['soundcloud']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertTrue(tag['src'].startswith('https://w.soundcloud.com/player/?'))
        self.assertFalse(tag.has_attr('style'))  # Verify removed


class ParseTextTest(unittest.TestCase):

    def test_blockquote(self):
        self.assertEqual({'text': {'raw': u"<p>Testing some text «ταБЬℓσ» we're 20% done!</p>"}},
                         parse_text(read_tag_data('text-paragraph')))

    def test_extra_editor_types(self):
        self.assertEqual([{'text': {'raw': '<blockquote><p>blockquote</p></blockquote>'}},
                         {'text': {'raw': '<ol>\n<li>one</li>\n<li>two</li>\n</ol>'}},
                         {'text': {'raw': '<ul>\n<li>bullet one</li>\n<li>bullet two</li>\n</ul>'}},
                         {'text': {'raw': '<h4>subheading</h4>'}},
                         {'text': {'raw': '<h3>heading</h3>'}}],
                         parse_body(read_data('editor-types')))


class ParseTwitterTest(unittest.TestCase):

    def test_blockquote(self):
        tag = parse_raw_tag(parse_twitter(
            read_tag_data('twitter-blockquote'))['twitter']['blockquote'])
        self.assertEqual('blockquote', tag.name)
        self.assertEqual(['twitter-tweet'], tag['class'])

    def test_widget(self):
        tag = parse_raw_tag(parse_twitter(read_tag_data('twitter-widget'))['twitter']['blockquote'])
        self.assertEqual('blockquote', tag.name)
        self.assertEqual(['twitter-tweet'], tag['class'])

    def test_video(self):
        tag = parse_raw_tag(parse_twitter_video(read_tag_data('twitter-video'))['twitter']['blockquote'])
        self.assertEqual('blockquote', tag.name)
        self.assertEqual(['twitter-video'], tag['class'])


class ParseVimdeoTest(unittest.TestCase):

    def test_parse(self):
        tag = parse_raw_tag(parse_vimeo(read_tag_data('vimeo'))['vimeo']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertEqual('https://player.vimeo.com/video/166544005', tag['src'])
        self.assertFalse(tag.has_attr('style'))  # Verify removed


class ParseYoutubeTest(unittest.TestCase):

    def test_iframe(self):
        self.assertEqual({'youtube': {'video_id': 'A1LF-LP_-uY'}},
                         parse_youtube(read_tag_data('youtube-iframe')))

    def test_no_iframe(self):
        self.assertEqual({'youtube': {'video_id': '2RcbUMPz3Dg'}},
                         parse_youtube(read_tag_data('youtube-no-iframe')))
