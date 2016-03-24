import logging

from django.db import models, transaction

from djes.models import Indexable

from bulbs.content.models import Content, ElasticsearchImageField

from .mixins import AnswerMixin, PollMixin


logger = logging.getLogger(__name__)


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


class Poll(Content, PollMixin):

    # This keeps Poll out of Content.search_objects
    class Mapping(Content.Mapping):
        poll_image = ElasticsearchImageField()

        class Meta():
            orphaned = True


class Answer(Indexable, AnswerMixin):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    class Mapping:
        answer_image = ElasticsearchImageField()

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
