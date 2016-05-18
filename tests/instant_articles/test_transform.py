import os.path
from django.test import TestCase
from django.test.utils import override_settings

from bulbs.instant_articles.transform import transform
from bulbs.instant_articles.renderer import InstantArticleRenderer


def read_data(*parts):
    here = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(here, 'test_data', *parts)).read()


@override_settings(BETTY_IMAGE_URL='http://images.onionstatic.com/starwipe')
class InstantArticleTransformTest(TestCase):

    def test_betty(self):
        actual = transform(read_data('input/betty.html'), InstantArticleRenderer())
        actual = actual.replace('\n', '')

        expected = read_data('output/betty.html').strip()
        self.assertEqual(expected.strip(),
                         actual.strip())
