from models import Poll, Answer
from bulbs.content.serializers import ContentSerializer

class PollSerializer(ContentSerializer):

    class Meta:
        model = Poll

class AnswerSerializer(ContentSerializer):

    class Meta:
        model = Answer
