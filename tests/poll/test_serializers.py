from bulbs.poll.models      import Poll, Answer
from bulbs.poll.serializers import PollSerializer, AnswerSerializer
from bulbs.utils.test       import (
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
        poll = Poll.objects.create(question_text='good text',
                title=random_title())
        serializer = PollSerializer(poll)
        self.assertEqual(serializer.data['id'], poll.id)
        self.assertEqual(serializer.data['question_text'], poll.question_text)
        self.assertEqual(serializer.data['title'], poll.title)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_poll_answer_serialization(self):
        poll = Poll.objects.create(question_text=u'good text',
                title=random_title())
        answer1 = Answer.objects.create(poll=poll, answer_text=u'this is some text')
        answer2 = Answer.objects.create(poll=poll, answer_text=u'forest path')
        serializer = PollSerializer(poll)
        answers_data = serializer.data['answers']
        self.assertEqual(answers_data, [
            {
                'id': u'1',
                'answer_text': answer1.answer_text,
            },
            {
                'id': u'2',
                'answer_text': answer2.answer_text,
            },
        ])

class AnswerTestCase(BaseIndexableTestCase):

    """ Tests for the 'AnswerSerializer'"""

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_answer_serialization(self):
        poll = Poll.objects.create(question_text='good text',
                title=random_title())
        answer = Answer.objects.create(poll=poll, answer_text='this is some text')
        serializer = AnswerSerializer(answer)
        self.assertEqual(serializer.data['answer_text'], answer.answer_text)

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_multiple_answer_serialization(self):
        poll = Poll.objects.create(question_text='good text',
                title=random_title())
        answer1 = Answer.objects.create(poll=poll, answer_text='this is some text')
        answer2 = Answer.objects.create(poll=poll, answer_text='forest path')
        serializer = AnswerSerializer(Answer.objects.all(), many=True)
        self.assertEqual(serializer.data[0]['answer_text'], answer1.answer_text)
        self.assertEqual(serializer.data[1]['answer_text'], answer2.answer_text)
