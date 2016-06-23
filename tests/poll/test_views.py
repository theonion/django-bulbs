from datetime import timedelta
import json
import re
import requests
import requests_mock
from six import PY2

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.content.models import Content
from bulbs.poll.models import Poll, Answer
from bulbs.utils.test import (
    random_title,
    BaseAPITestCase,
)
from bulbs.utils.test.make_vcr import make_vcr
from bulbs.utils.test.mock_vault import mock_vault

from .common import SECRETS

vcr = make_vcr(__file__)  # Define vcr file path


class PollAPITestCase(BaseAPITestCase):
    """ Test for Poll API """

    def setUp(self):
        super(PollAPITestCase, self).setUp()
        Content.search_objects.refresh()

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('poll-list')
        self.assertEqual(list_url, '/api/v1/poll/')
        detail_url = reverse('poll-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/v1/poll/1/')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_sodahead_service_failure(self):
        with requests_mock.Mocker() as mocker:
            sodahead_endpoint = re.compile('https://onion.sodahead.com/api/polls/')
            mocker.post(sodahead_endpoint, status_code=500)
            list_url = reverse('poll-list')
            data = {
                'questions_text': 'go underneath the bridge!',
                'title': random_title()
            }
            self.give_permissions()
            response = self.api_client.post(
                list_url,
                json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 503)

    @mock_vault(SECRETS)
    def test_search_polls(self):
        with vcr.use_cassette('test_search_polls'):
            poll1 = Poll.objects.create(
                question_text='find me',
                title=random_title(),
            )
            Poll.objects.create(
                question_text='dont find me',
                title=random_title(),
            )
        Poll.search_objects.refresh()

        self.give_permissions()
        list_url = reverse('poll-list') + '?search=' + poll1.title

        response = self.api_client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['question_text'], 'find me')

    @mock_vault(SECRETS)
    def test_filter_to_active_polls(self):
        with vcr.use_cassette('test_filter_to_active_polls'):
            Poll.objects.create(
                question_text='find me',
                title=random_title(),
                published=(timezone.now() - timedelta(1)),
            )
            poll2 = Poll.objects.create(
                question_text='dont find me',
                title=random_title(),
            )
            poll2.published = timezone.now() + timedelta(2)
            poll2.save()
        Poll.search_objects.refresh()

        self.give_permissions()
        list_url = reverse('poll-list') + '?active=true'
        response = self.api_client.get(list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['question_text'], 'find me')

    @mock_vault(SECRETS)
    def test_filter_to_closed_polls(self):
        with vcr.use_cassette('test_filter_to_closed_polls'):
            poll1 = Poll.objects.create(
                question_text='find me',
                title=random_title(),
                published=(timezone.now() - timedelta(2)),
            )
            Poll.objects.create(
                question_text='dont find me',
                title=random_title(),
            )
            poll1.end_date = timezone.now() - timedelta(1)
            poll1.save()
        Poll.search_objects.refresh()

        self.give_permissions()
        list_url = reverse('poll-list') + '?closed=true'
        response = self.api_client.get(list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['question_text'], 'find me')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_post_to_create_poll(self):
        list_url = reverse('poll-list')
        data = {
            'question_text': 'go underneath the bridge!',
            'title': random_title()
        }
        self.give_permissions()
        response = self.api_client.post(list_url, json.dumps(data), content_type='application/json')
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
        self.give_permissions()
        response = self.api_client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], poll.id)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_put_proctected(self):
        poll = Poll.objects.create(
            question_text='decent text',
            title=random_title(),
        )
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        response = self.api_client.put(
            detail_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_put_to_update_poll(self):
        poll = Poll.objects.create(
            question_text='decent text',
            title=random_title(),
        )
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        data = {
            'question_text': 'better text',
            'title': random_title(),
            'published': timezone.now().isoformat(),
            'end_date': (timezone.now() + timedelta(10)).isoformat(),
        }
        self.give_permissions()
        response = self.api_client.put(
            detail_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poll.objects.get(id=poll.id).question_text, 'better text')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_delete_poll(self):
        poll = Poll.objects.create(question_text='good text', title=random_title())
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        self.give_permissions()
        response = self.api_client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        response2 = self.api_client.get(detail_url)
        self.assertEqual(response2.data['detail'], u'Not found.')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_set_end_date_to_null(self):
        poll = Poll.objects.create(question_text='dont end this poll', title=random_title())
        poll.published = timezone.now()
        poll.end_date = timezone.now() + timedelta(1)
        poll.save()

        data = {
            'published': poll.published.isoformat(),
            'title': poll.title,
            'question_text': poll.question_text,
            'end_date': None,
        }

        self.give_permissions()
        detail_url = reverse('poll-detail', kwargs={'pk': poll.id})
        response = self.api_client.put(
            detail_url,
            data=json.dumps(data),
            content_type='application/json',
        )

        response = requests.get(
            'https://onion.sodahead.com/api/polls/{}'.format(poll.sodahead_id)
        ).json()
        self.assertIsNone(response['poll']['endDate'])


class AnswerAPITestCase(BaseAPITestCase):
    """ Test for Answer API """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_router_registered(self):
        list_url = reverse('answer-list')
        self.assertEqual(list_url, '/api/v1/poll-answer/')
        detail_url = reverse('answer-detail', kwargs={'pk': 1})
        self.assertEqual(detail_url, '/api/v1/poll-answer/1/')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_post_to_answers(self):
        poll = Poll.objects.create(question_text='Russell\'s time was over', title=random_title())
        answers_url = reverse('answer-list')
        data = {
            'poll': poll.id,
            'answer_text': 'he\'s getting stale'
        }
        self.give_permissions()
        response = self.api_client.post(
            answers_url,
            json.dumps(data),
            content_type='application/json'
        )
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
        self.give_permissions()
        response = self.api_client.put(
            answer_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.get(id=answer.id).answer_text, 'he\'s getting stale')

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_delete_answer(self):
        poll = Poll.objects.create(question_text='dreams', title=random_title())
        answer = Answer.objects.create(answer_text='are fun', poll=poll)
        answer_url = reverse('answer-detail', kwargs={'pk': answer.id})
        self.give_permissions()
        response = self.api_client.delete(answer_url)
        self.assertEqual(response.status_code, 204)
        response2 = self.api_client.get(answer_url)
        self.assertEqual(response2.data['detail'], u'Not found.')


class GetPollDataTestCase(BaseAPITestCase):
    """
        Test for public get poll data.
        returns json that includes vote counts.
    """

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_get_poll_data(self):
        poll = Poll.objects.create(
            question_text=u'are we on vox!?',
            title=random_title()
        )
        Answer.objects.create(poll=poll, answer_text=u'affirmative')
        Answer.objects.create(poll=poll, answer_text=u'that is a negatory')

        poll_data_url = reverse('get-merged-poll-data', kwargs={'pk': poll.id})
        response = self.api_client.get(
            poll_data_url,
            **{'HTTP_ORIGIN': 'this.cool.origin'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], 'this.cool.origin')
        self.assertEqual(response['Access-Control-Allow-Credentials'], 'true')

        if PY2:
            data = json.loads(response.content)
        else:
            data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(data['id'], poll.id)
        self.assertEqual(data['total_votes'], 0)

        self.assertEqual(data['answers'][0]['total_votes'], 0)
        self.assertIsNotNone(data['answers'][0]['sodahead_id'], 0)

        self.assertEqual(data['answers'][1]['total_votes'], 0)
        self.assertIsNotNone(data['answers'][1]['sodahead_id'], 0)
