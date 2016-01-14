from bulbs.poll.models import Poll, Answer
from bulbs.utils.test  import BaseIndexableTestCase, \
                              make_vcr, mock_vault, \
                              random_title

import os
import random
import re
import requests
import requests_mock
import simplejson as json

from bulbs.utils import vault

from .common import SECRETS

vcr = make_vcr(__file__)  # Define vcr file path

class PollTestCase(BaseIndexableTestCase):

    """ Tests for the Poll model class """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_create(self):
        poll = Poll.objects.create(question_text='good text', title=random_title())
        self.assertTrue(Poll.objects.filter(id=poll.id).exists())


    @vcr.use_cassette('test_create')
    @mock_vault(SECRETS)
    def test_poll_creation_gets_sodahead_id(self):
        poll = Poll.objects.create(question_text='other text', title=random_title())
        self.assertNotEqual(poll.sodahead_id, '')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_poll_creation_fails_when_sodahead_request_fails(self):
        sodahead_endpoint = re.compile('https://onion.sodahead.com/api/polls/[\d]+/')
        with requests_mock.Mocker() as mocker:
            mocker.post('https://onion.sodahead.com/api/polls/', status_code=666)
            with self.assertRaises(Poll.SodaheadResponseError):
                Poll.objects.create(question_text='other text', title=random_title())

class AnswerTestCase(BaseIndexableTestCase):

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_create_answer(self):
        poll = Poll.objects.create(question_text='collins adventure', title=random_title())
        answer = Answer.objects.create(poll=poll)
        self.assertEqual(answer.sodahead_answer_id, 'answer_01')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_multiple_answer_creation(self):
        poll = Poll.objects.create(question_text='melissas adventure', title=random_title())
        answer1 = Answer.objects.create(poll=poll, answer_text='something')
        answer2 = Answer.objects.create(poll=poll, answer_text='bridge')
        answer3 = Answer.objects.create(poll=poll, answer_text='alibaster')
        response = requests.get('https://onion.sodahead.com/api/polls/{}'.format(poll.sodahead_id)).json()
        self.assertEqual(len(response['poll']['answers']), 3)
        self.assertEqual(response['poll']['answers'][0]['title'], 'something')
        self.assertEqual(response['poll']['answers'][1]['title'], 'bridge')
        self.assertEqual(response['poll']['answers'][2]['title'], 'alibaster')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_handles_blank_answer_text(self):
        poll = Poll.objects.create(question_text='listening to your heart', title=random_title())
        answer = Answer.objects.create(poll=poll, answer_text='')
        response = requests.get('https://onion.sodahead.com/api/polls/{}'.format(poll.sodahead_id)).json()
        self.assertEqual(response['poll']['answers'][0]['title'], 'Intentionally blank')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_handles_blank_answer_text(self):
        sodahead_endpoint = re.compile('https://onion.sodahead.com/api/polls/[\d]+/')
        poll = Poll.objects.create(question_text='listening to your heart', title=random_title())
        with requests_mock.Mocker() as mocker:
            mocker.post(sodahead_endpoint, status_code=666)
            with self.assertRaises(Poll.SodaheadResponseError):
                Answer.objects.create(poll=poll, answer_text='something')
