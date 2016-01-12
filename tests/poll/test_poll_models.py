from bulbs.poll.models import Poll, Answer
from bulbs.utils.test import BaseIndexableTestCase

class PollModelTestCase(BaseIndexableTestCase):
    """ A Test Suite for Poll model """

    def test_create_poll(self):
        poll = Poll.objects.create()
        self.assertTrue(Poll.objects.filter(id=poll.id).exists())

class AnswerModelTestCase(BaseIndexableTestCase):
    """ A Test Suite for Answer model """

    def test_create_answer(self):
        poll = Poll.objects.create()
        answer = Answer.objects.create(
            poll=poll
        )
        self.assertTrue(Poll.objects.filter(id=poll.id).exists())
