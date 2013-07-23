import datetime
import itertools

from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from .models import Content, TestContentObj, TestContentObjTwo


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
                published=one_hour_ago
            )
            obj2 = TestContentObjTwo.objects.create(
                title=' '.join(reversed(combo)),
                description=' '.join(combo),
                foo=combo[0],
                bar=i,
                published=one_hour_ago
            )

    def test_content_subclasses(self):
        # We created one of each subclass per combination so the following should be true:
        self.assertEqual(Content.objects.count(), len(self.combos) * self.num_subclasses)
        self.assertEqual(TestContentObj.objects.count(), len(self.combos))
        self.assertEqual(TestContentObjTwo.objects.count(), len(self.combos))

    def test_content_list_view(self):
        client = Client()
        response = client.get('/content_list_one.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['object_list']), len(self.combos) * self.num_subclasses)

    def test_num_polymorphic_queries(self):
        with self.assertNumQueries(1 + self.num_subclasses):
            for content in Content.objects.all():
                self.assertIsInstance(content, (TestContentObj, TestContentObjTwo))

    # def test_content_detail_view(self):
    #     client = Client()
    #     for content in Content.objects.all():
    #         response = client.get(content.get_absolute_url())
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['object'].pk, content.pk)
    #         # make sure we get the subclass, not the super
    #         self.assertIsInstance(content, (TestContentObj, TestContentObjTwo))

