import logging
import pytz
import requests

from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from elasticsearch_dsl.filter import Range
from rest_framework.exceptions import APIException

from djes.models import Indexable

from bulbs.content.filters import Published
from bulbs.content.models import Content, ContentManager
from bulbs.utils import vault

logger = logging.getLogger(__name__)

SODAHEAD_DATE_FORMAT = '%m/%d/%y %I:%M %p'

SODAHEAD_POLL_ENDPOINT = '{}/api/polls/{{}}/'.format(settings.SODAHEAD_BASE_URL)
SODAHEAD_POLLS_ENDPOINT = '{}/api/polls/'.format(settings.SODAHEAD_BASE_URL)
SODAHEAD_DELETE_POLL_ENDPOINT = '{}/api/polls/{{}}/?access_token={{}}'.format(
    settings.SODAHEAD_BASE_URL
)

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

    def __init__(self, detail):
        self.detail = detail


class SodaheadResponseFailure(APIException):
    status_code = 400
    default_detail = "Error from third-party poll provider"

    def __init__(self, detail):
        self.detail = detail


def Closed():  # noqa
    end_date_params = {
        "lte": timezone.now(),
    }

    return Range(end_date=end_date_params)


class PollManager(ContentManager):
    def search(self, **kwargs):
        search_query = super(PollManager, self).search(**kwargs)

        if "active" in kwargs:
            search_query = search_query.filter(Published(before=timezone.now()))

        if "closed" in kwargs:
            search_query = search_query.filter(Closed())

        return search_query


class Poll(Content):
    search_objects = PollManager()

    question_text = models.TextField(blank=True, default="")
    sodahead_id = models.CharField(max_length=20, blank=True, default="")
    last_answer_index = models.IntegerField(default=0)
    end_date = models.DateTimeField(null=True, default=None)

    # This keeps Poll out of Content.search_objects
    class Mapping(Content.Mapping):
        class Meta():
            orphaned = True

    def get_sodahead_data(self):
        response = requests.get(SODAHEAD_POLL_ENDPOINT.format(self.sodahead_id))

        if not response.ok:
            logger.error(
                'Poll(id: %s, sodahead_id: %s).get_sodahead_data status_code: %s error: %s',
                self.id,
                self.sodahead_id,
                response.text,
                response.status_code,
            )
            return {
                'poll': {
                    'totalVotes': 0,
                    'answers': [],
                },
            }
        else:
            return response.json()

    def get_sodahead_token(self):
        return vault.read(settings.SODAHEAD_TOKEN_VAULT_PATH)['value']

    def sodahead_payload(self):
        payload = {
            'access_token': self.get_sodahead_token(),
            'name': self.title,
            'title': self.question_text,
        }

        if self.sodahead_id:
            payload['id'] = self.sodahead_id

        if self.published:
            activation_date = self.published.astimezone(pytz.utc)
            payload['activationDate'] = activation_date.strftime(SODAHEAD_DATE_FORMAT)
        else:
            payload['activationDate'] = None

        if self.end_date:
            end_date = self.end_date.astimezone(pytz.utc)
            payload['endDate'] = end_date.strftime(SODAHEAD_DATE_FORMAT)
        else:
            payload['endDate'] = ''

        for answer in self.answers.all():
            if answer.answer_text and answer.answer_text is not u'':
                payload[answer.sodahead_answer_id] = answer.answer_text
            else:
                payload[answer.sodahead_answer_id] = BLANK_ANSWER

        if 'answer_01' not in payload:
            payload['answer_01'] = DEFAULT_ANSWER_1

        if 'answer_02' not in payload:
            payload['answer_02'] = DEFAULT_ANSWER_2

        return payload

    def save(self, *args, **kwargs):
        if not self.sodahead_id:
            response = requests.post(SODAHEAD_POLLS_ENDPOINT, self.sodahead_payload())

            if response.ok:
                self.sodahead_id = response.json()['poll']['id']
            elif response.status_code > 499:
                raise SodaheadResponseError(response.text)
            else:
                raise SodaheadResponseFailure(response.text)
        else:
            self.sync_sodahead()

        super(Poll, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        response = requests.delete(
            SODAHEAD_DELETE_POLL_ENDPOINT.format(
                self.sodahead_id,
                self.get_sodahead_token(),
            )
         )
        if response.status_code > 499:
            raise SodaheadResponseError(response.text)
        elif response.status_code > 399:
            raise SodaheadResponseFailure(response.text)
        super(Poll, self).delete(*args, **kwargs)

    def sync_sodahead(self):
        response = requests.post(
            SODAHEAD_POLL_ENDPOINT.format(self.sodahead_id),
            self.sodahead_payload()
        )

        if response.status_code > 499:
            raise SodaheadResponseError(response.json())
        elif response.status_code > 399:
            raise SodaheadResponseFailure(response.json())


class Answer(Indexable):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    sodahead_answer_id = models.CharField(max_length=20, blank=True, default="")
    answer_text = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        # using transaction/select_for_update here because we don't want to
        # run this block in parallel. If we did, we would end up with answers
        # with the same value for `answer.sodahead_answer_id`.
        # This is because we are deriving sodahead_answer_id based on the count
        # of answers that have ever been created for an poll.
        #   (see top of file for in depth explainer)
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
