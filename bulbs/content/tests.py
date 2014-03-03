from __future__ import absolute_import

import itertools
import datetime

from django.utils import timezone
from django.test.client import Client
from django.template.defaultfilters import slugify

from bulbs.content.models import Content, Tag
from bulbs.content.serializers import ContentSerializer
from bulbs.indexable.tests import BaseIndexableTestCase

from tests.testcontent.models import TestContentObj, TestContentObjTwo


class SerializerTestCase(BaseIndexableTestCase):

    def test_tag_serializer(self):
        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        test_obj = TestContentObj(
            title='Testing Tag Serialization',
            description='Serialization shouldn\'t be so hard',
            published=one_hour_ago,
            feature_type='Some Bullshit',
            foo='Ugh'
        )
        test_obj.save(index=False)

        some_tag = Tag.objects.create(name='Some Tag')

        self.assertEqual(ContentSerializer(test_obj).data['tags'], [])
        test_obj.tags.add(some_tag)

        self.assertEqual(ContentSerializer(test_obj).data['tags'][0]['name'], "Some Tag")

        # Now let's test updating an object via a serializer
        data = {
            "tags": [
                {
                    "id": some_tag.id,
                    "slug": "some-tag",
                    "name": "Some Tag"
                },
                {
                    "slug": "some-other-tag",
                    "name": "Some Other Tag"
                }
            ]
        }
        serializer = ContentSerializer(test_obj, data=data, partial=True)
        self.assertEqual(serializer.is_valid(), True)
        serializer.save()
        self.assertEqual(test_obj.tags.count(), 2)
        self.assertEqual(Tag.objects.all().count(), 2)

        some_other_tag = Tag.objects.get(slug="some-other-tag")

        ## Let's remove one of the tags from the object
        data = {
            "tags": [
                {
                    "id": some_other_tag.id,
                    "slug": "some-other-tag",
                    "name": "Some Other Tag"
                }
            ]
        }
        serializer = ContentSerializer(test_obj, data=data, partial=True)
        self.assertEqual(serializer.is_valid(), True)
        serializer.save()
        self.assertEqual(test_obj.tags.count(), 1)
        self.assertEqual(Tag.objects.all().count(), 2)


class PolyContentTestCase(BaseIndexableTestCase):
    def setUp(self):
        super(PolyContentTestCase, self).setUp()
        """
        Normally, the "Content" class picks up available doctypes from installed apps, but
        in this case, our test models don't exist in a real app, so we'll hack them on.
        """

        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        words = ['spam', 'driver', 'dump truck', 'restaurant']
        self.num_subclasses = 2
        self.combos = list(itertools.combinations(words, 2))
        self.all_tags = []
        for i, combo in enumerate(self.combos):
            tags = []
            for atom in combo:
                tag, created = Tag.objects.get_or_create(name=atom, slug=slugify(atom))
                tags.append(tag)
                self.all_tags.append(tag)
            obj = TestContentObj.objects.create(
                title=' '.join(combo),
                description=' '.join(reversed(combo)),
                foo=combo[0],
                published=one_hour_ago,
                feature_type='Obj one'
            )
            obj.tags.add(*tags)
            obj.index()
            obj2 = TestContentObjTwo.objects.create(
                title=' '.join(reversed(combo)),
                description=' '.join(combo),
                foo=combo[1],
                bar=i,
                published=one_hour_ago,
                feature_type='Obj two'
            )
            obj2.tags.add(*tags)
            obj2.index()

        # We need to let the index refresh
        TestContentObj.search_objects.refresh()
        TestContentObjTwo.search_objects.refresh()

    def test_filter_search_content(self):

        self.assertEqual(Content.objects.count(), 12)

        q = Content.search_objects.search()
        self.assertEqual(q.count(), 12)

        q = Content.search_objects.search(tags=["spam"])
        self.assertEqual(q.count(), 6)
        for content in q.full():
            self.assertTrue("spam" in content.tags.values_list("slug", flat=True))

        q = Content.search_objects.search(feature_types=["obj-one"])
        self.assertEqual(q.count(), 6)
        for content in q.full():
            self.assertEqual("Obj one", content.feature_type)

        q = Content.search_objects.search(types=["testcontent_testcontentobj"])
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(types=["testcontent_testcontentobjtwo"]).full()
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(types=[
            "testcontent_testcontentobjtwo", "testcontent_testcontentobj"])
        self.assertEqual(q.count(), 12)

    def test_negative_filters(self):
        q = Content.search_objects.search(tags=["-spam"])
        self.assertEqual(q.count(), 6)

        q = Content.search_objects.search(feature_types=["-obj-one"])
        self.assertEqual(q.count(), 6)
        for content in q.full():
            self.assertNotEqual("Obj one", content.feature_type)

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

    def test_add_remove_tags(self):
        content = Content.objects.all()[0]
        original_tag_count = len(content.tags.all())
        new_tag = Tag.objects.create(name='crankdat')
        content.tags.add(new_tag)
        self.assertEqual(len(content.tags.all()), original_tag_count + 1)
        self.assertEqual(len(content.tags.all()), len(content.extract_document()['tags']))

    def test_search_exact_name_tags(self):
        Tag.objects.create(name='Beeftank')
        self.es.refresh()
        results = Tag.search_objects.query(name__match='beeftank').full()
        self.assertTrue(len(results) > 0)
        tag_result = results[0]
        self.assertIsInstance(tag_result, Tag)

    def test_in_bulk_performs_polymorphic_query(self):
        content_ids = [c.id for c in Content.objects.all()]
        results = Content.objects.in_bulk(content_ids)
        subclasses = tuple(Content.__subclasses__())
        for result in results.values():
            self.assertIsInstance(result, subclasses)

    def test_deserialize_none(self):
        s = Content.get_serializer_class()(data=None)
        s.data
