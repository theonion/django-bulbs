from bulbs.content.serializers import ContentSerializer
from rest_framework import serializers
from models import Poll, Answer

class PollSerializer(ContentSerializer):

    class Meta:
        model = Poll

class AnswerSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=20)
    answer_text = serializers.CharField()
