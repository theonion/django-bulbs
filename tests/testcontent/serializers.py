from .models import TestContentObj, TestContentObjTwo, TestContentDetailImage

from bulbs.content.serializers import ContentSerializer, ImageFieldSerializer


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

    detail_image = ImageFieldSerializer(caption_field="detail_alt", alt_field="detail_alt")

    class Meta:
        model = TestContentDetailImage
