from .models import TestContentObj, TestContentObjTwo

from bulbs.content.serializers import ContentSerializer


class TestContentObjSerializer(ContentSerializer):
    """Serializes the ExternalLink model."""

    class Meta:
        model = TestContentObj


class TestContentObjTwoSerializer(ContentSerializer):
    """Serializes the ExternalLink model."""

    class Meta:
        model = TestContentObjTwo
