from bulbs.content.models import Content
from bulbs.utils import vault
from django.db import models
from djes.models import Indexable
from rest_framework.exceptions import APIException

from time import mktime
import requests

class Poll(Content):
    class SodaheadResponseError(APIException):
        status_code = 503
        default_detail = "Third-party poll provider temporarily unavailable."

    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")
    last_answer_index = models.IntegerField(default=0)

    def sodahead_payload(self):
        poll_payload = {
            'access_token': vault.read('sodahead/token'),
            'id': self.sodahead_id,
            'name': self.title,
            'title': self.question_text,
        }

        #if self.published:
        #    activation_date = self.published.isoformat()
        #    poll_payload['activationDate'] = activation_date

        for answer in self.answers.all():
            if answer.answer_text is u'':
                poll_payload[answer.sodahead_answer_id] = 'Intentionally blank'
            else:
                poll_payload[answer.sodahead_answer_id] = answer.answer_text

        if not 'answer_01' in poll_payload:
            poll_payload['answer_01'] = 'default answer 1'

        if not 'answer_02' in poll_payload:
            poll_payload['answer_02'] = 'default answer 2'

        return poll_payload

    def save(self, *args, **kwargs):
        if self.sodahead_id is "":
            response = requests.post('https://onion.sodahead.com/api/polls/', self.sodahead_payload())
            if response.status_code is not 200:
                raise Poll.SodaheadResponseError(response.text)
            else:
                self.sodahead_id = response.json()['poll']['id']
        else:
            self.sync_sodahead()

        super(Poll, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        response = requests.delete('https://onion.sodahead.com/api/polls/{}/?access_token={}'
                .format(self.sodahead_id, vault.read('sodahead/token')))
        if response.status_code is not 204:
            raise Poll.SodaheadResponseError(response.text)
        super(Poll, self).delete(*args, **kwargs)

    def sync_sodahead(self):
        response = requests.post('https://onion.sodahead.com/api/polls/{}/'
                .format(self.sodahead_id), self.sodahead_payload())
        if response.status_code is not 200:
            raise Poll.SodaheadResponseError(response.text)

class Answer(Indexable):
    poll = models.ForeignKey(Poll,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    sodahead_answer_id = models.CharField(max_length=20, blank=True, default="")
    answer_text = models.TextField(blank=True, default="")


    def save(self, *args, **kwargs):
        if self.sodahead_answer_id is "":
            count = self.poll.last_answer_index
            self.sodahead_answer_id = 'answer_%02d' % (count + 1)
        super(Answer, self).save(*args, **kwargs)
        self.poll.last_answer_index += 1
        self.poll.save()
        self.poll.sync_sodahead()
