import json
import sys

from django.core.urlresolvers import reverse
from django.test import TestCase

from bulbs.poll.models import Poll, Answer
from bulbs.utils.test  import make_vcr, random_title, \
                              mock_vault

from .common import SECRETS

vcr = make_vcr(__file__)  # Define vcr file path

class PollAPITestCase(TestCase):
    """ Test for Poll API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('poll-list')
        self.assertEqual(list_url, '/api/polls/')
        detail_url = reverse('poll-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/polls/1/')

class AnswerAPITestCase(TestCase):
    """ Test for Answer API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('answer-list')
        self.assertEqual(list_url, '/api/answers/')
        detail_url = reverse('answer-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/answers/1/')
