from bulbs.utils.test import BaseIndexableTestCase

from bulbs.poll.models import Poll

class PollTestCase(BaseIndexableTestCase):

    """ Tests for the Poll model class """

    def test_create(self):
        poll = Poll.objects.create(question_text='good text')
        self.assertTrue(Poll.objects.filter(id=poll.id).exists())

