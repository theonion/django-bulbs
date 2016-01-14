from bulbs.poll.models      import Poll, Answer
from bulbs.poll.serializers import PollSerializer, AnswerSerializer
from bulbs.utils.test       import BaseIndexableTestCase, \
                                   make_vcr, mock_vault, \
                                   random_title

import os

SECRETS = {
    'sodahead/token': os.environ.get("SODAHEAD_API_TOKEN", "")
}

vcr = make_vcr(__file__)  # Define vcr file path

class PollSerializerTestCase(BaseIndexableTestCase):

    """Tests for the `PollSerializer`"""

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_poll_serialization(self):
        poll = Poll.objects.create(question_text='good text',
                title=random_title())
        serializer = PollSerializer(poll)
        import ipdb; ipdb.set_trace()
        self.assertEqual(serializer.data['id'], poll.id)
        self.assertEqual(serializer.data['question_text'], poll.question_text)
        self.assertEqual(serializer.data['name'], poll.title)

class AnswerTestCase(BaseIndexableTestCase):

    """ Tests for the 'AnswerSerializer'"""

    @vcr.use_cassette()
    @mock_vault(SECRETS)
    def test_answer_serialization(self):
        poll = Poll.objects.create(question_text='good text',
                title=random_title())
        answer = Answer.objects.create(poll=poll, answer_text='this is some text')
        serializer = AnswerSerializer(poll)
        self.assertEqual(serializer.data['answer_01'], answer.answer_text)
