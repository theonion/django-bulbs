import unittest

from bs4 import BeautifulSoup

from bulbs.instant_articles.parser import (parse_betty,
                                           parse_content,
                                           # parse_element,
                                           parse_instagram)


class ParseContentTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], parse_content(''))


def make_element(html):
    return [c for c in BeautifulSoup(html.strip())][0]


# class ParseElementTest(unittest.TestCase):

#     def test_empty(self):
#         self.assertIsNone([], parse_element(''))


class ParseBettyTest(unittest.TestCase):

    def test_match(self):
        self.assertEqual(
            {'betty': {'image_id': '29938'}},
            parse_betty(make_element("""
                <figure class="thumb">
                    <div
                     class="image"
                     data-type="image"
                     data-image-id="29938"
                     >
                        <div></div>
                        <noscript>
                            <img src="http://i.onionstatic.com/clickhole/2993/8/16x9/600.jpg">
                        </noscript>
                    </div>
                </figure>
            """)))


class ParseInstagramTest(unittest.TestCase):

    def test_match(self):
        IFRAME = '<iframe class="instagram-media instagram-media-rendered"></iframe>'
        self.assertEqual({'instagram': {'iframe': IFRAME}},
                         parse_instagram(make_element(IFRAME)))
