import os.path
import unittest

from bs4 import BeautifulSoup

from bulbs.instant_articles.parser import (parse_betty,
                                           parse_body,
                                           # parse_tag,
                                           # parse_instagram,
                                           parse_youtube,
                                           )


def read_data(name):
    here = os.path.dirname(os.path.realpath(__file__))
    html = open(os.path.join(here, 'test_data', 'input', name + '.html')).read()
    return [c for c in BeautifulSoup(html.strip()).children][0]


class ParseBodyTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], parse_body(''))


# class ParseTagTest(unittest.TestCase):

#     def test_empty(self):
#         self.assertIsNone([], parse_tag(''))


class ParseBettyTest(unittest.TestCase):

    def test_match(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u"Testing «ταБЬℓσ» we're 20% done!"}},
                         parse_betty(read_data('betty-caption')))

    def test_missing_caption(self):
        self.assertEqual({'betty': {'image_id': '9513',
                                    'caption': u''}},
                         parse_betty(read_data('betty-no-caption')))


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
