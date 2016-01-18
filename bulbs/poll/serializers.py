from bulbs.content.serializers import ContentSerializer
from rest_framework import serializers
from models import Poll, Answer

class AnswerSerializer(serializers.ModelSerializer):
    poll = serializers.PrimaryKeyRelatedField(
        queryset=Poll.objects.all(),
        required=False
    )
    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'poll')

class PollSerializer(ContentSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
