from .models import TestContentObj, TestContentObjTwo, TestContentDetailImage, TestLiveBlog

from bulbs.content.serializers import ContentSerializer
from bulbs.liveblog.serializers import LiveBlogSerializerMixin

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


class TestLiveBlogSerializer(ContentSerializer, LiveBlogSerializerMixin):

    class Meta:
        model = TestLiveBlog
