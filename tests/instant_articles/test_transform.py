import os.path

from mock import patch
import six

from django.test import TestCase

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
        actual = actual.strip()
        expected = read_data('output/{}.html'.format(name)).strip()
        if six.PY2:
            # Force unicode
            expected = expected.decode('utf-8')

        self.assertEqual(expected, actual)

    def test_multiple(self):
        with patch('djbetty.storage.settings.BETTY_IMAGE_URL',
                   'http://images.onionstatic.com/starwipe'):
            self.check_embed('body-multiple')

    def test_example_avc_article(self):
        self.check_embed('avclub-example')

    def test_betty(self):
        with patch('djbetty.storage.settings.BETTY_IMAGE_URL',
                   'http://images.onionstatic.com/starwipe'):
            self.check_embed('betty-caption')
            self.check_embed('betty-no-caption')

    def test_facebook(self):
        self.check_embed('facebook-post')
        self.check_embed('facebook-video')

    def test_imgur(self):
        self.check_embed('imgur')

    def test_instagram(self):
        self.check_embed('instagram-blockquote')
        self.check_embed('instagram-iframe')

    def test_onion_video(self):
        self.check_embed('onion_video')

    def test_soundcloud(self):
        self.check_embed('soundcloud')

    def test_text(self):
        self.check_embed('text-paragraph')

    def test_twitter(self):
        self.check_embed('twitter-blockquote')
        self.check_embed('twitter-widget')

    def test_vimeo(self):
        self.check_embed('vimeo')

    def test_youtube(self):
        self.check_embed('youtube-iframe')
        self.check_embed('youtube-no-iframe')
