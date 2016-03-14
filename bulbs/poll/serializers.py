import re

from rest_framework import serializers

from bulbs.content.serializers import ContentSerializer

from .models import Poll, Answer


class AnswerSerializer(serializers.ModelSerializer):
    poll = serializers.PrimaryKeyRelatedField(
        queryset=Poll.objects.all(),
        required=False
    )

    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'poll',)


class PollSerializer(ContentSerializer):
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
            index += 1

        return representation
