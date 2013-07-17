from rest_framework import serializers
from bulbs.polycontent.serializers import ContentSerializer, PolyContentSerializer
from .models import Content, TestContentObj, TestContentObjTwo


class TestContentObjSerializer(ContentSerializer):
	"""Serializes TestContentObjs."""
	class Meta:
		model = TestContentObj


class TestContentObjTwoSerializer(ContentSerializer):
	"""Serializes TestContentObjTwos."""
	class Meta:
		model = TestContentObjTwo


class TestPolyContentSerializer(PolyContentSerializer):
	"""Serializes polymorphic test content."""
	child_serializers = (
		(TestContentObj, TestContentObjSerializer),
		(TestContentObjTwo, TestContentObjTwoSerializer),
	)

