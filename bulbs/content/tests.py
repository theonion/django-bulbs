import itertools
import datetime
import json

from django.test import TestCase
from django.utils import timezone
from django.test.client import Client
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from elasticutils.contrib.django import get_es

from bulbs.content.models import Content, Tag, fetch_cached_models_by_id
from bulbs.content.management import sync_es


class TestContentObj(Content):
    """Fake content here"""
    foo = models.CharField(max_length=255)

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class TestContentObjTwo(Content):
    """Come and get your fake content"""
    foo = models.CharField(max_length=255)
    bar = models.IntegerField()

    def get_absolute_url(self):
        return '/detail/%s/' % self.pk


class PolyContentTestCase(TestCase):
    def setUp(self):

        """
        Normally, the "Content" class picks up available doctypes from installed apps, but
        in this case, our test models don't exist in a real app, so we'll hack them on.
        """
        for model in [TestContentObj, TestContentObjTwo]:
            Content._cache[model.get_mapping_type_name()] = model
        sync_es(None)  # We should pass "bulbs.content.models" here, but for now this is fine.
        
        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        words = ['spam', 'driver', 'dump truck', 'restaurant']
        self.num_subclasses = 2
        self.combos = list(itertools.combinations(words, 2))
        self.all_tags = []
        for i, combo in enumerate(self.combos):
            for atom in combo:
                tag = Tag(name=atom)
                tag.save()
                self.all_tags.append(tag)
            obj = TestContentObj.objects.create(
                title=' '.join(combo),
                description=' '.join(reversed(combo)),
                foo=combo[0],
                published=one_hour_ago,
                feature_type='Obj one'
            )
            obj.tags.add(*self.all_tags)
            obj2 = TestContentObjTwo.objects.create(
                title=' '.join(reversed(combo)),
                description=' '.join(combo),
                foo=combo[0],
                bar=i,
                published=one_hour_ago,
                feature_type='Obj two'
            )
            obj2.tags.add(*self.all_tags)

    def tearDown(self):
        es = get_es(urls=settings.ES_URLS)
        es.delete_index(settings.ES_INDEXES.get('default', 'testing'))

    def test_serialize_id(self):
        c = Content.objects.all()[0]
        c_id = c.from_source(c.extract_document()).id
        self.assertNotEqual(c_id, None)

    def test_serialize_idempotence(self):
        c = Content.objects.all()[0]
        self.assertEqual(
            c.extract_document(),
            c.__class__.from_source(c.extract_document()).extract_document()
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

    def test_add_remove_tags(self):
        content = Content.objects.all()[0]
        original_tag_count = len(content.tags.all())
        new_tag = Tag(name='crankdat')
        new_tag.save()
        self.all_tags.append(new_tag) # save it for later tests
        content.tags.add(new_tag)
        self.assertEqual(len(content.tags.all()), original_tag_count + 1)
        self.assertEqual(len(content.tags.all()), len(content.extract_document()['tags']))

    def test_search_exact_name_tags(self):
        tag = Tag(name='Beeftank')
        tag.save(index=True, refresh=True)
        self.all_tags.append(tag) # save it for later tests
        results = Tag.objects.search(name='beeftank')
        self.assertEqual(len(results), 1)
        tag_result = results[0]
        self.assertIsInstance(tag_result, Tag)

    def test_content_tag_management_view(self):
        content = Content.objects.all()[0]
        content_tag_names = set([tag.name for tag in content.tags.all()])
        # get tags
        client = Client()
        tag_url = reverse('bulbs.content.views.manage_content_tags', kwargs={'pk': content.pk})
        response = client.get(tag_url)
        data = json.loads(response.content)
        self.assertEqual(len(data), len(content_tag_names))
        # add tag
        response = client.post(tag_url, {
            'tag': 'Chowdah'
        })
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Chowdah')
        new_content_tag_names = set([tag.name for tag in content.tags.all()])
        self.assertEqual(len(new_content_tag_names - content_tag_names), 1)
        self.assertIn('Chowdah', new_content_tag_names)
        # remove tag
        response = client.delete(tag_url + '?tag=Chowdah')
        new_content_tag_names = set([tag.name for tag in content.tags.all()])
        self.assertEqual(len(new_content_tag_names - content_tag_names), 0)

    def test_in_bulk_performs_polymorphic_query(self):
        content_ids = [c.id for c in Content.objects.all()]
        results = Content.objects.in_bulk(content_ids)
        subclasses = tuple(Content.__subclasses__())
        for result in results.values():
            self.assertIsInstance(result, subclasses)

    def test_deserialize_none(self):
        s = Content.get_serializer_class()(data=None)
        d = s.data

    def test_filter_search_content(self):
        tag = self.all_tags[0]
        q = Content.objects.search(tags=[tag.slug])
        self.assertNotEqual([], list(q))
        feature_type = Content.objects.all()[0].feature_type
        q = Content.objects.search(feature_types=[feature_type])
        self.assertNotEqual([], list(q))

    def test_fetch_cached_models(self):
        all_objs = list(Content.objects.all())
        ids = [obj.id for obj in Content.objects.all()]
        with self.assertNumQueries(3):
            results = fetch_cached_models_by_id(Content, ids)
        # make sure we got everything we wanted
        self.assertEqual(all_objs, results)
        # ensure we get the results from cache on the 2nd query
        with self.assertNumQueries(0):
            results = fetch_cached_models_by_id(Content, ids)
        # and that the cached entries are correct
        self.assertEqual(all_objs, results)

    def test_tag_model_faceting(self):
        s = Tag.objects.search()
        s = s.facet('id')
        results = s.model_facet_counts(Tag)
        for r in results:
            self.assertTrue(hasattr(r, 'facet_count'))

