import unittest

from bs4 import BeautifulSoup

from bulbs.instant_articles.parser import (parse_betty,
                                           parse_body,
                                           # parse_tag,
                                           # parse_instagram,
                                           # parse_youtube,
                                           )


class ParseBodyTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], parse_body(''))


def make_tag(html):
    return [c for c in BeautifulSoup(html).body.children][0]


# class ParseTagTest(unittest.TestCase):

#     def test_empty(self):
#         self.assertIsNone([], parse_tag(''))


class ParseBettyTest(unittest.TestCase):

    def test_match(self):
        self.assertEqual(
            {'betty': {'image_id': '29938'}},
            parse_betty(make_tag("""
                <div
                    class="image"
                    data-type="image"
                    data-image-id="29938">
                    <div></div>
                    <noscript>
                        <img src="http://i.onionstatic.com/clickhole/2993/8/16x9/600.jpg">
                    </noscript>
                </div>
            """)))


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
