# -*- coding: utf-8 -*-

import os.path
import unittest

from bs4 import BeautifulSoup

from bulbs.instant_articles.parser import (parse_betty,
                                           parse_body,
                                           parse_facebook,
                                           parse_instagram,
                                           parse_onion_video,
                                           parse_text,
                                           parse_twitter,
                                           parse_youtube,
                                           )


def parse_raw_tag(html):
    return [c for c in BeautifulSoup(html.strip()).children][0]


def read_data(name):
    here = os.path.dirname(os.path.realpath(__file__))
    html = open(os.path.join(here, 'test_data', 'input', name + '.html')).read()
    return parse_raw_tag(html)


class ParseBodyTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], parse_body(''))


# class ParseTagTest(unittest.TestCase):

#     def test_empty(self):
#         self.assertIsNone([], parse_tag(''))


class ParseFacebookTest(unittest.TestCase):

    def test_post(self):
        tag = parse_raw_tag(parse_facebook(read_data('facebook-post'))['facebook']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertTrue(tag['src'].startswith('https://www.facebook.com/plugins/post.php?'))
        self.assertFalse(tag.has_attr('style'))  # Verify removed

    def test_video(self):
        tag = parse_raw_tag(parse_facebook(read_data('facebook-video'))['facebook']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertTrue(tag['src'].startswith('https://www.facebook.com/plugins/video.php?'))
        self.assertFalse(tag.has_attr('style'))  # Verify removed


class ParseBettyTest(unittest.TestCase):

    def test_match(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u"Testing «ταБЬℓσ» we're 20% done!"}},
                         parse_betty(read_data('betty-caption')))

    def test_missing_caption(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u''}},
                         parse_betty(read_data('betty-no-caption')))


class ParseInstagramTest(unittest.TestCase):

    def test_iframe(self):
        self.assertEqual({'instagram': {'instagram_id': '3ewOSHitL2'}},
                         parse_instagram(read_data('instagram-iframe')))

    def test_blockquote(self):
        self.assertEqual({'instagram': {'instagram_id': '3jeiuICtD7'}},
                         parse_instagram(read_data('instagram-blockquote')))


class ParseOnionVideoTest(unittest.TestCase):

    def test_parse(self):
        tag = parse_raw_tag(parse_onion_video(read_data('onion_video'))['onion_video']['iframe'])
        self.assertEqual('iframe', tag.name)
        self.assertEqual(['onionstudios-playlist'], tag['class'])


class ParseTextTest(unittest.TestCase):

    def test_blockquote(self):
        self.assertEqual({'text': {'raw': u"<p>Testing some text «ταБЬℓσ» we're 20% done!</p>"}},
                         parse_text(read_data('text-paragraph')))


class ParseTwitterTest(unittest.TestCase):

    def test_blockquote(self):
        tag = parse_raw_tag(parse_twitter(read_data('twitter-blockquote'))['twitter']['blockquote'])
        self.assertEqual('blockquote', tag.name)
        self.assertEqual(['twitter-tweet'], tag['class'])

    def test_widget(self):
        tag = parse_raw_tag(parse_twitter(read_data('twitter-widget'))['twitter']['blockquote'])
        self.assertEqual('blockquote', tag.name)
        self.assertEqual(['twitter-tweet'], tag['class'])


class ParseYoutubeTest(unittest.TestCase):

    def test_iframe(self):
        self.assertEqual({'youtube': {'video_id': 'A1LF-LP_-uY'}},
                         parse_youtube(read_data('youtube-iframe')))

    def test_no_iframe(self):
        self.assertEqual({'youtube': {'video_id': '2RcbUMPz3Dg'}},
                         parse_youtube(read_data('youtube-no-iframe')))

# class ParseInstagramTest(unittest.TestCase):

#     def test_match(self):
#         IFRAME = '<iframe class="instagram-media instagram-media-rendered"></iframe>'
#         self.assertEqual({'instagram': {'iframe': IFRAME}},
#                          parse_instagram(make_tag(IFRAME)))


# class ParseYoutubeTest(unittest.TestCase):

#     def test_match(self):
#         IFRAME = '<iframe class="instagram-media instagram-media-rendered"></iframe>'
#         self.assertEqual({'youtube': {'video_id': '23fh23'}},
#                          parse_youtube(make_tag(IFRAME)))
