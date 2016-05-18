import os.path
import unittest

from bulbs.instant_articles.transform import transform
from bulbs.instant_articles.renderer import InstantArticleRenderer


def read_data(*parts):
    here = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(here, 'test_data', *parts)).read()


class TransformTest(unittest.TestCase):

    def test_one_element(self):
        actual = transform(read_data('input/betty.html'), InstantArticleRenderer())
        expected = read_data('output/betty.html').strip()
        # TODO: Compare HTML (need to strip whitespace + such
        self.assertEqual(expected.strip(),
                         actual.strip())
