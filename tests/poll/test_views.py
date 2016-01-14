import json
import sys

from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Poll, Answer

from .common import SECRETS

class PollAPITestCase(TestCase):
    """ Test for Poll API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('poll-list')
        self.assertEqual(list_url, '/api/polls/')
        detail_url = reverse('poll-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/polls/1/')

class AnswerPITestCase(TestCase):
    """ Test for Poll API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('poll-list')
        self.assertEqual(list_url, '/api/polls/')
        detail_url = reverse('poll-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/polls/1/')
