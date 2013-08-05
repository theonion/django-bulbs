import datetime
import itertools

from django.test import TestCase
from django.test.client import Client
from django.utils import timezone

from .models import (
    Content, ReadonlyRelatedManager, ROBud, Tag, TestContentObj, TestContentObjTwo
)


class PolyContentTestCase(TestCase):
    def setUp(self):
        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        words = ['spam', 'driver', 'dump truck', 'restaurant']
        self.num_subclasses = 2
        self.combos = list(itertools.combinations(words, 2))
        for i, combo in enumerate(self.combos):
            tags = []
            for atom in combo:
                tag = Tag(name=atom)
                tag.save()
                tags.append(tag)
            obj = TestContentObj.objects.create(
                title=' '.join(combo),
                description=' '.join(reversed(combo)),
                foo=combo[0],
                published=one_hour_ago
            )
            obj.tags.add(*tags)
            obj2 = TestContentObjTwo.objects.create(
                title=' '.join(reversed(combo)),
                description=' '.join(combo),
                foo=combo[0],
                bar=i,
                published=one_hour_ago
            )
            obj2.tags.add(*tags)

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

    def test_readonly_related_manager(self):
        r = ROBud()
        r.foo = ['bar', 'schlub']
        self.assertEqual(2, len(r.foo.all()))
        with self.assertRaises(TypeError):
            r.foo.add('tagz')
        with self.assertRaises(TypeError):
            r.foo.clear()
        with self.assertRaises(TypeError):
            r.foo.remove('bar')

    def test_readonly_tags(self):
        readonly_content= Content.search()[0]
        real_content = Content.objects.get(id=readonly_content.id)
        self.assertIsInstance(readonly_content.tags, ReadonlyRelatedManager)
        self.assertEqual(
            len(readonly_content.tags.all()),
            len(real_content.tags.all())
        )

    def test_add_remove_tags(self):
        real_content = Content.objects.all()[0]
        original_tag_count = len(real_content.tags.all())
        new_tag = Tag(name='crankdat')
        new_tag.save()
        real_content.tags.add(new_tag)
        self.assertEqual(len(real_content.tags.all()), original_tag_count + 1)
        readonly_content = Content.search(pk=real_content.id)[0]
        self.assertEqual(
            len(readonly_content.tags.all()),
            len(real_content.tags.all())
        )

        
    # def test_content_detail_view(self):
    #     client = Client()
    #     for content in Content.objects.all():
    #         response = client.get(content.get_absolute_url())
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['object'].pk, content.pk)
    #         # make sure we get the subclass, not the super
    #         self.assertIsInstance(content, (TestContentObj, TestContentObjTwo))

