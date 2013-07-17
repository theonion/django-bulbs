from rest_framework import serializers

from .models import Content


class PolymorphicSerializer(object):
	"""Serializes polymorphic querysets."""
	child_serializers = []

	def __init__(self, data, many=False):
		self.many = many
		self._data = data
		self._serializer_map = {
			model: serializer for model, serializer in self.child_serializers
		}
		if not self._serializer_map:
			raise ValueError('Hey Alan Turing, you need to configure some child serializers.')

	@property
	def data(self):
		if not self.many:
			self._data = [self._data]
		results = []
		for instance in self._data:
			serializer_class = self._serializer_map.get(instance.__class__, None)
			# fail early, fail often.
			if not serializer_class:
				raise ValueError(
					'Model "%s" has no serializer configured.' % instance.__class__.__name__)
			# Brute force instead of a clever subclass:
			serializer = serializer_class(instance)
			results.append(serializer.data)

		if self.many:
			return results
		else:
			if results:
				return results[0]
			return None


class ContentSerializer(serializers.ModelSerializer):
	"""Base serializer of Content."""
	class Meta:
		model = Content

