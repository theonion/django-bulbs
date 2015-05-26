from .models import TestContentObj, TestContentObjTwo, TestContentDetailImage

from bulbs.content.serializers import ContentSerializer

from djbetty.serializers import ImageFieldSerializer


class TestContentObjSerializer(ContentSerializer):
    """Serializes the ExternalLink model."""

    class Meta:
        model = TestContentObj


class TestContentObjTwoSerializer(ContentSerializer):
    """Serializes the ExternalLink model."""

    class Meta:
        model = TestContentObjTwo


class TestContentDetailImageSerializer(ContentSerializer):
    """Serializes the ExternalLink model."""

    detail_image = ImageFieldSerializer()

    class Meta:
        model = TestContentDetailImage
