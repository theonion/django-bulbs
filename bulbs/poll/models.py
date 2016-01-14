from bulbs.content.models import Content
from bulbs.utils import vault
from django.db import models
from djes.models import Indexable
from exceptions import Exception

import requests

class Poll(Content):
    class SodaheadResponseError(Exception):
        pass

    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")

    def sodahead_payload(self):
        return {
                'access_token': vault.read('sodahead/token'),
                'name': self.title,
                'title': self.question_text,
                'answer_01': 'default answer 1',
                'answer_02': 'default answer 2'
                }

    def sodahead_answer_payload(self):
        poll_payload = {
                'access_token': vault.read('sodahead/token'),
                'id': self.sodahead_id
                }

        for answer in self.answer_set.all():
            if answer.answer_text is u'':
                poll_payload[answer.sodahead_answer_id] = 'Intentionally blank'
            else:
                poll_payload[answer.sodahead_answer_id] = answer.answer_text

        return poll_payload

    def save(self, *args, **kwargs):
        if self.sodahead_id is "":
            response = requests.post('https://onion.sodahead.com/api/polls/', self.sodahead_payload())
            if response.status_code is not 200:
                raise Poll.SodaheadResponseError(response.text)
            else:
                self.sodahead_id = response.json()['poll']['id']

        super(Poll, self).save(*args, **kwargs)

    def sync_sodahead(self):
        response = requests.post('https://onion.sodahead.com/api/polls/{}/'
                .format(self.sodahead_id), self.sodahead_answer_payload())
        if response.status_code is not 200:
            raise Poll.SodaheadResponseError(response.text)

class Answer(Indexable):
    poll = models.ForeignKey(Poll,
        on_delete=models.CASCADE
    )
    sodahead_answer_id = models.CharField(max_length=20, blank=True, default="")
    answer_text = models.TextField(blank=True, default="")


    def save(self, *args, **kwargs):
        if self.sodahead_answer_id is "":
            count = self.poll.answer_set.count()
            self.sodahead_answer_id = 'answer_%02d' % (count + 1)
        super(Answer, self).save(*args, **kwargs)
        self.poll.sync_sodahead()
