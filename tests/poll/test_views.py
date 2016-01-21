import json
import sys

from django.core.urlresolvers import reverse
from django.test import TestCase

from bulbs.poll.models import Poll, Answer
from bulbs.utils.test  import (
    make_vcr,
    random_title,
    mock_vault
)

import re
import requests_mock

from .common import SECRETS

vcr = make_vcr(__file__)  # Define vcr file path

class PollAPITestCase(TestCase):
    """ Test for Poll API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('poll-list')
        self.assertEqual(list_url, '/poll/')
        detail_url = reverse('poll-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/poll/1/')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_sodahead_service_failure(self):
        with requests_mock.Mocker() as mocker:
            sodahead_endpoint = re.compile('https://onion.sodahead.com/api/polls/')
            mocker.post(sodahead_endpoint, status_code=666)
            list_url = reverse('poll-list')
            data = {
                'questions_text': 'go underneath the bridge!',
                'title': random_title()
            }
            response = self.client.post(list_url, json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 503)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_post_to_create_poll(self):
        list_url = reverse('poll-list')
        data = {
            'question_text': 'go underneath the bridge!',
            'title': random_title()
        }
        response = self.client.post(list_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        id = response.data.get('id')
        self.assertIsNotNone(id)
        poll = Poll.objects.get(id=int(id))
        self.assertIsNotNone(poll)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_get_poll(self):
        poll = Poll.objects.create(question_text='good text', title=random_title())
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], poll.id)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_put_to_update_poll(self):
        poll = Poll.objects.create(question_text='decent text', title=random_title())
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        data = {
            'question_text': 'better_text',
            'title': random_title()
        }
        response = self.client.put(detail_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poll.objects.get(id=poll.id).question_text, 'better_text')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_delete_poll(self):
        poll = Poll.objects.create(question_text='good text', title=random_title())
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        response2 = self.client.get(detail_url)
        self.assertEqual(response2.data['detail'], u'Not found.')

class AnswerAPITestCase(TestCase):
    """ Test for Answer API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('answer-list')
        self.assertEqual(list_url, '/answer/')
        detail_url = reverse('answer-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/answer/1/')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_sodahead_service_failure(self):
        poll = Poll.objects.create(question_text='it is time for Russell', title=random_title())
        with requests_mock.Mocker() as mocker:
            sodahead_endpoint = re.compile('https://onion.sodahead.com/api/polls/')
            mocker.post(sodahead_endpoint, status_code=666)
            list_url = reverse('answer-list')
            data = {
                'poll': poll.id,
                'answer_text': 'he is ready'
            }

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_post_to_answers(self):
        poll = Poll.objects.create(question_text='Russell\'s time was over', title=random_title())
        answers_url = reverse('answer-list')
        data = {
            'poll': poll.id,
            'answer_text': 'he\'s getting stale'
        }
        response = self.client.post(answers_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_put_to_update_answer(self):
        poll = Poll.objects.create(question_text='Russell actually never was', title=random_title())
        answer = Answer.objects.create(answer_text='isn\'t that disturbing?', poll=poll)
        answer_url = reverse('answer-detail', kwargs={'pk': answer.id})
        data = {
            'answer_text': 'he\'s getting stale'
        }
        response = self.client.put(answer_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.get(id=answer.id).answer_text, 'he\'s getting stale')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_delete_answer(self):
        poll = Poll.objects.create(question_text='dreams', title=random_title())
        answer = Answer.objects.create(answer_text='are fun', poll=poll)
        answer_url = reverse('answer-detail', kwargs={'pk': answer.id})
        response = self.client.delete(answer_url)
        self.assertEqual(response.status_code, 204)
        response2 = self.client.get(answer_url)
        self.assertEqual(response2.data['detail'], u'Not found.')
