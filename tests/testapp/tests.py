import datetime
import itertools

from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from .models import Content, TestContentObj, TestContentObjTwo
from .serializers import (
	ContentSerializer, TestContentObjSerializer, TestPolyContentSerializer
)


class PolyContentTestCase(TestCase):
	def setUp(self):
		# generate some data
		one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
		words = ['spam', 'driver', 'dump truck', 'restaurant']
		self.num_subclasses = 2
		self.combos = list(itertools.combinations(words, 2))
		for i, combo in enumerate(self.combos):
			obj = TestContentObj.objects.create(
				title=' '.join(combo),
				description=' '.join(reversed(combo)),
				foo=combo[0],
				time_published=one_hour_ago
			)
			obj2 = TestContentObjTwo.objects.create(
				title=' '.join(reversed(combo)),
				description=' '.join(combo),
				foo=combo[0],
				bar=i,
				time_published=one_hour_ago
			)

	def test_content_subclasses(self):
		# We created one of each subclass per combination so the following should be true:
		self.assertEqual(Content.objects.count(), len(self.combos) * self.num_subclasses)
		self.assertEqual(TestContentObj.objects.count(), len(self.combos))
		self.assertEqual(TestContentObjTwo.objects.count(), len(self.combos))

	def test_polycontent_list_view(self):
		client = Client()
		response = client.get('/content_list_one.html')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			len(response.context['object_list']), len(self.combos) * self.num_subclasses)

	def test_num_polymorphic_queries(self):
		with self.assertNumQueries(1 + self.num_subclasses):
			for content in Content.objects.all():
				self.assertIsInstance(content, (TestContentObj, TestContentObjTwo))

	def test_polycontent_detail_view(self):
		client = Client()
		for content in Content.objects.all():
			response = client.get(content.get_absolute_url())
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.context['object'].pk, content.pk)
			# make sure we get the subclass, not the super
			self.assertIsInstance(content, (TestContentObj, TestContentObjTwo))

	def test_content_serializers(self):
		# make sure submodel queries only fetch the submodel subtree
		queryset = TestContentObj.objects.all()
		serializer = TestContentObjSerializer(queryset, many=True)
		self.assertEqual(len(serializer.data), len(self.combos))
		
		queryset = Content.objects.all()
		serializer = ContentSerializer(queryset, many=True)
		self.assertEqual(
			len(serializer.data), len(self.combos) * self.num_subclasses)

	def test_polymorphic_serializer(self):
		queryset = Content.objects.all()
		serializer = TestPolyContentSerializer(queryset, many=True)
		# count the number of times different model fields show up in the results
		foo_count = 0
		bar_count = 0
		for result in serializer.data:
			if 'foo' in result:
				foo_count += 1
			if 'bar' in result:
				bar_count += 1
		# every subclass has a foo field		
		self.assertEqual(foo_count, len(self.combos) * self.num_subclasses)
		# only one of the content types has a bar field
		self.assertEqual(bar_count, len(self.combos))

