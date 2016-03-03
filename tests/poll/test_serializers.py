from datetime import timedelta

from django.utils import timezone

from bulbs.poll.models import Poll, Answer
from bulbs.poll.serializers import (
    PollPublicSerializer,
    PollSerializer,
    AnswerSerializer,
)
from bulbs.utils.test import (
    BaseIndexableTestCase,
    make_vcr,
    mock_vault,
    random_title,
)
from .common import SECRETS

vcr = make_vcr(__file__)  # Define vcr file path


class PollSerializerTestCase(BaseIndexableTestCase):

    """Tests for the `PollSerializer`"""

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_poll_serialization(self):
        poll = Poll.objects.create(
            question_text='good text',
            title=random_title(),
            published=timezone.now(),
            end_date=timezone.now() + timedelta(1),
         )
        serializer = PollSerializer(poll)
        self.assertEqual(serializer.data['id'], poll.id)
        self.assertEqual(serializer.data['question_text'], poll.question_text)
        self.assertEqual(serializer.data['title'], poll.title)
        self.assertIsNotNone(serializer.data['end_date'])

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_poll_answer_serialization(self):
        poll = Poll.objects.create(
            question_text=u'good text',
            title=random_title(),
        )
        Answer.objects.create(poll=poll, answer_text=u'this is some text')
        Answer.objects.create(poll=poll, answer_text=u'forest path')
        serializer = PollSerializer(poll)
        answers_data = serializer.data['answers']

        self.assertEqual(answers_data[0]['id'], 1)
        self.assertEqual(answers_data[0]['answer_text'], u'this is some text')
        self.assertEqual(answers_data[0]['poll'], 1)

        self.assertEqual(answers_data[1]['id'], 2)
        self.assertEqual(answers_data[1]['answer_text'], u'forest path')
        self.assertEqual(answers_data[1]['poll'], 1)


class PollPublicSerializerTestCase(BaseIndexableTestCase):

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_serialization_includes_sodahead_data(self):
        poll = Poll.objects.create(
            question_text='is it powerful?',
            title=random_title(),
        )
        Answer.objects.create(poll=poll, answer_text=u'yes')
        answer2 = Answer.objects.create(poll=poll, answer_text=u'no')
        Answer.objects.create(poll=poll, answer_text=u'maybe')

        serializer = PollPublicSerializer(Poll.objects.get(id=poll.id))
        answers_data = serializer.data['answers']
        first_sodahead_id = answers_data[0]['sodahead_id']
        second_sodahead_id = answers_data[1]['sodahead_id']
        third_sodahead_id = answers_data[2]['sodahead_id']

        self.assertEqual(answers_data[0]['id'], 1)
        self.assertEqual(answers_data[0]['sodahead_id'], first_sodahead_id)
        self.assertEqual(answers_data[0]['answer_text'], u'yes')
        self.assertEqual(answers_data[0]['poll'], 1)
        self.assertEqual(answers_data[0]['total_votes'], 0)

        self.assertEqual(answers_data[1]['id'], 2)
        self.assertEqual(answers_data[1]['sodahead_id'], second_sodahead_id)
        self.assertEqual(answers_data[1]['answer_text'], u'no')
        self.assertEqual(answers_data[1]['poll'], 1)
        self.assertEqual(answers_data[1]['total_votes'], 0)

        self.assertEqual(answers_data[2]['id'], 3)
        self.assertEqual(answers_data[2]['sodahead_id'], third_sodahead_id)
        self.assertEqual(answers_data[2]['answer_text'], u'maybe')
        self.assertEqual(answers_data[2]['poll'], 1)
        self.assertEqual(answers_data[2]['total_votes'], 0)

        answer2.delete()

        serializer = PollPublicSerializer(Poll.objects.get(id=poll.id))
        answers_data = serializer.data['answers']

        self.assertEqual(answers_data[0]['id'], 1)
        self.assertEqual(answers_data[0]['sodahead_id'], first_sodahead_id)
        self.assertEqual(answers_data[0]['answer_text'], u'yes')
        self.assertEqual(answers_data[0]['poll'], 1)
        self.assertEqual(answers_data[0]['total_votes'], 0)

        self.assertEqual(answers_data[1]['id'], 3)
        self.assertEqual(answers_data[1]['sodahead_id'], third_sodahead_id)
        self.assertEqual(answers_data[1]['answer_text'], u'maybe')
        self.assertEqual(answers_data[1]['poll'], 1)
        self.assertEqual(answers_data[1]['total_votes'], 0)


class AnswerSerializerTestCase(BaseIndexableTestCase):

    """ Tests for the 'AnswerSerializer'"""

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_answer_serialization(self):
        poll = Poll.objects.create(
            question_text='good text',
            title=random_title(),
        )
        answer = Answer.objects.create(poll=poll, answer_text='this is some text')
        serializer = AnswerSerializer(answer)
        self.assertEqual(serializer.data['answer_text'], answer.answer_text)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_multiple_answer_serialization(self):
        poll = Poll.objects.create(
            question_text='good text',
            title=random_title(),
        )
        answer1 = Answer.objects.create(poll=poll, answer_text='this is some text')
        answer2 = Answer.objects.create(poll=poll, answer_text='forest path')
        serializer = AnswerSerializer(Answer.objects.all(), many=True)
        self.assertEqual(serializer.data[0]['answer_text'], answer1.answer_text)
        self.assertEqual(serializer.data[1]['answer_text'], answer2.answer_text)
