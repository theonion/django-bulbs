import re

from rest_framework import serializers

from djbetty.serializers import ImageFieldSerializer

from bulbs.content.serializers import ContentSerializer
from .models import Poll, Answer


class AnswerSerializer(serializers.ModelSerializer):
    answer_image = ImageFieldSerializer(required=False, allow_null=True,)
    poll = serializers.PrimaryKeyRelatedField(
        queryset=Poll.objects.all(),
        required=False
    )

    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'poll', 'answer_image',)


class PollSerializer(ContentSerializer):
    poll_image = ImageFieldSerializer(required=False)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        exclude = ('thumbnail_override',)


class PollPublicSerializer(PollSerializer):
    def to_representation(self, poll):
        representation = super(PollSerializer, self).to_representation(poll)
        sodahead_data = poll.get_sodahead_data()
        representation['total_votes'] = sodahead_data['poll']['totalVotes']
        index = 0
        for answer in poll.answers.all():
            sodahead_index = int(re.findall(r'\d+', answer.sodahead_answer_id)[0]) - 1
            sodahead_answer = sodahead_data['poll']['answers'][sodahead_index]
            representation['answers'][index]['sodahead_id'] = sodahead_answer['id']
            representation['answers'][index]['total_votes'] = sodahead_answer['totalVotes']
            if answer.answer_image:
                representation['answers'][index]['answer_image_url'] = answer.answer_image.get_crop_url(ratio='1x1')
            index += 1

        return representation
