from bulbs.utils.test import BaseIndexableTestCase

from bulbs.poll.models import Poll

import vcr
import os

def make_vcr(test_path, record_mode='once'):
    base_dir = os.path.dirname(os.path.realpath(test_path))
    test_name =  os.path.splitext(test_path)[0]
    cassette_dir = os.path.join(base_dir, 'test_data/cassettes', test_name)
    return vcr.VCR(
            cassette_library_dir=cassette_dir,
            ignore_hosts=[],
            record_mode=record_mode,
    )

class PollTestCase(BaseIndexableTestCase):

    """ Tests for the Poll model class """

    def test_create(self):
        poll = Poll.objects.create(question_text='good text')
        self.assertTrue(Poll.objects.filter(id=poll.id).exists())

    vcr = make_vcr(__file__)

    @vcr.use_cassette()

    def test_poll_creation_gets_sodahead_id(self):
         poll = Poll.objects.create(question_text='other text')
         self.assertNotEqual(poll.sodahead_id, '')
