import os.path
from django.test import TestCase
from django.test.utils import override_settings

from bulbs.instant_articles.transform import transform
from bulbs.instant_articles.renderer import InstantArticleRenderer


def read_data(*parts):
    here = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(here, 'test_data', *parts)).read()


class InstantArticleTransformTest(TestCase):

    maxDiff = None

    def check_embed(self, name):
        actual = transform(read_data('input/{}.html'.format(name)),
                           InstantArticleRenderer())
        actual = actual.replace('\n', '')

        expected = read_data('output/{}.html'.format(name)).strip()
        self.assertEqual(expected.strip(),
                         actual.strip())

    @override_settings(BETTY_IMAGE_URL='http://images.onionstatic.com/starwipe')
    def test_betty(self):
        self.check_embed('betty-caption')
        self.check_embed('betty-no-caption')

    def test_instagram(self):
        self.check_embed('instagram-blockquote')
        self.check_embed('instagram-iframe')

    def test_twitter(self):
        self.check_embed('twitter-blockquote')
        self.check_embed('twitter-widget')

    def test_youtube(self):
        self.check_embed('youtube-iframe')
        self.check_embed('youtube-no-iframe')

    def test_onion_video(self):
        self.check_embed('onion_video')
