from bulbs.content.models import Content
from bulbs.utils import vault
from django.db import models, transaction
from djes.models import Indexable
from rest_framework.exceptions import APIException

from time import mktime
import pytz
import requests

SODAHEAD_DATE_FORMAT = '%m/%d/%y %I:%M %p'

SODAHEAD_POLL_ENDPOINT = 'https://onion.sodahead.com/api/polls/{}/'
SODAHEAD_POLLS_ENDPOINT = 'https://onion.sodahead.com/api/polls/'
SODAHEAD_DELETE_POLL_ENDPOINT = 'https://onion.sodahead.com/api/polls/{}/?access_token={}'

BLANK_ANSWER = 'Intentionally blank'
DEFAULT_ANSWER_1 = 'default answer 1'
DEFAULT_ANSWER_2 = 'default answer 2'


"""
Sodahead API Integration Rationale

The sodahoad api implements a POST and a PUT endpoint.

In the payload to these endpoints, answers are keyed

answer_0n      => "Question 1 Text"
answer_0n+1    => "Question 2 Text"
answer_0n+...  => "Question 3 Text"

Or however many answers you would like.

Sodahead provides no way to re-order/delete these answers.

So everytime we create an answer, we want to increment
the associated answer key.

This is especially tricky, as if we have the following
answers:

In the context of a single Poll:

poll.models.Poll(pk=1)

poll.models.Answer(pk=1) => answer_01
poll.models.Answer(pk=2) => answer_02
poll.models.Answer(pk=3) => answer_03

And we delete Answer(pk=2)

The next answer needs to be

poll.models.Answer(pk=5) => answer_04

So we cannot merely add up the answers of a poll, we
have to keep track of how many answers we have already
created.

This is done by the field `last_answer_index` on the Poll model.

It is incremented by 1 every time an Answer is saved.
"""

class SodaheadResponseError(APIException):
    status_code = 503
    default_detail = "Third-party poll provider temporarily unavailable."

class Poll(Content):

    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")
    last_answer_index = models.IntegerField(default=0)
    end_date = models.DateTimeField(null=True, default=None)

    def get_sodahead_data(self):
        response = requests.get(SODAHEAD_POLL_ENDPOINT.format(self.sodahead_id))

        if response.status_code != 200:
            raise SodaheadResponseError(response.text)
        else:
            return response.json()

    def sodahead_payload(self):
        poll_payload = {
            'access_token': vault.read('sodahead/token')['value'],
            'id': self.sodahead_id,
            'name': self.title,
            'title': self.question_text,
        }

        if self.published:
            activation_date = self.published.astimezone(pytz.utc)
            poll_payload['activationDate'] = activation_date.strftime(SODAHEAD_DATE_FORMAT)

        if self.end_date:
            end_date = self.end_date.astimezone(pytz.utc)
            poll_payload['endDate'] = end_date.strftime(SODAHEAD_DATE_FORMAT)

        for answer in self.answers.all():
            if answer.answer_text == u'':
                poll_payload[answer.sodahead_answer_id] = BLANK_ANSWER
            else:
                poll_payload[answer.sodahead_answer_id] = answer.answer_text

        if not 'answer_01' in poll_payload:
            poll_payload['answer_01'] = DEFAULT_ANSWER_1

        if not 'answer_02' in poll_payload:
            poll_payload['answer_02'] = DEFAULT_ANSWER_2

        return poll_payload

    def save(self, *args, **kwargs):
        if not self.sodahead_id:
            response = requests.post(SODAHEAD_POLLS_ENDPOINT, self.sodahead_payload())
            if response.status_code != 200:
                raise SodaheadResponseError(response.text)
            else:
                self.sodahead_id = response.json()['poll']['id']
        else:
            self.sync_sodahead()

        super(Poll, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        response = requests.delete(SODAHEAD_DELETE_POLL_ENDPOINT
                .format(self.sodahead_id, vault.read('sodahead/token')['value']))
        if response.status_code != 204:
            raise SodaheadResponseError(response.text)
        super(Poll, self).delete(*args, **kwargs)

    def sync_sodahead(self):
        response = requests.post(SODAHEAD_POLL_ENDPOINT
                .format(self.sodahead_id), self.sodahead_payload())
        if response.status_code != 200:
            raise SodaheadResponseError(response.text)

class Answer(Indexable):
    poll = models.ForeignKey(Poll,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    sodahead_answer_id = models.CharField(max_length=20, blank=True, default="")
    answer_text = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            poll = Poll.objects.select_for_update().get(pk=self.poll_id)
            if self.sodahead_answer_id:
                super(Answer, self).save(*args, **kwargs)
            else:
                # See Rationale at top of file for in depth explanation
                # of what is going on here. We have to track how many answers
                # have ever been created for a Poll.
                # A simple count will not suffice because we dont want to 
                # re-use any answer keys.
                answer_index = poll.last_answer_index + 1
                self.sodahead_answer_id = 'answer_%02d' % (answer_index)
                super(Answer, self).save(*args, **kwargs)
                poll.last_answer_index += 1
                poll.save()
