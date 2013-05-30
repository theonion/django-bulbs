import itertools
import datetime
import json

from elasticutils import get_es, S

from django.test import TestCase as DBTestCase
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from bulbs.base.models import Contentish, Tagish
try:
    from testapp.models import TestContentObj, TestContentObjTwo
except:
    raise ImportError("Something with your test app isn't configured correctly")


class ESTestCase(DBTestCase):

    def setUp(self):
        # Create index, if necessary
        call_command('sync_es')
        self.es = get_es(urls=settings.ES_URLS)

    def tearDown(self):
        self.es.delete_index(settings.ES_INDEXES.get('default'))


class ContentCreationTestCases(ESTestCase):

    def test_no_tags(self):
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        no_tags = TestContentObj.objects.create(
            title="No Tags",
            field1="No",
            field2="Tags",
            tags=[],
            published=one_hour_ago)


class ContentishTestCase(ESTestCase):

    def setUp(self):
        super(ContentishTestCase, self).setUp()

        for tags in itertools.combinations(["Tag 1", "Tag 2", "Tag 3", "Tag 4"], 2):
            one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
            obj = TestContentObj.objects.create(
                title="Tags: %s, %s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                tags=tags,
                published=one_hour_ago)

            obj2 = TestContentObjTwo.objects.create(
                title="Tags: %s, %s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                field3=3,
                tags=tags,
                published=one_hour_ago)

        self.es.refresh()

    def test_facets(self):
        facet_counts = Contentish.search().facet('tags.slug').facet_counts()
        self.assertEqual(len(facet_counts['tags.slug']), 4)
        for facet in facet_counts['tags.slug']:
            self.assertEqual(facet['count'], 6)

    def test_content_search(self):
        results = Contentish.search()
        self.assertEqual(results.count(), 12)

        results = Contentish.search(tags=["tag-1"])
        self.assertEqual(len(results), 6)

        results = Contentish.search(tags=["tag-1", "tag-2"])
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertTrue(any(tag.slug == 'tag-1' for tag in result.tags))
            self.assertTrue(any(tag.slug == 'tag-2' for tag in result.tags))
            self.assertFalse(any(tag.slug == 'tag-3' for tag in result.tags))
            self.assertFalse(any(tag.slug == 'tag-4' for tag in result.tags))

        results = Contentish.search(types=[TestContentObjTwo])
        self.assertEqual(results.count(), 6)

        results = Contentish.search(types=[TestContentObj])
        self.assertEqual(len(results), 6)

        with self.assertRaises(AttributeError):
            results[0].tags = ['Some Tag', 'Some other tag']

        with self.assertRaises(AttributeError):
            results[0].feature_type = 'Some Feature Type'

        results = Tagish.search()
        self.assertEqual(results.count(), 4)

    def test_content_list_views(self):
        client = Client()
        response = client.get('/content_list_one.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 6)

        response = client.get('/content_list_one.html?tag=tag-1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 3)


class TagSearchTestCase(ESTestCase):
    def setUp(self):
        super(TagSearchTestCase, self).setUp()
        for name in ["Foo", "Bar", "Baz", "FooBar", "FooBaz", "A.V. Foo"]:
            tag = Tagish.from_name(name)
            tag.index()

        self.es.refresh()

    def test_tag_search(self):
        results = Tagish.search()
        self.assertEqual(results.count(), 6)

        results = Tagish.search('foo')
        self.assertEqual(results.count(), 4)

        results = Tagish.search('foob')
        self.assertEqual(results.count(), 2)

    def test_tag_search_view(self):
        client = Client()
        response = client.get('/base/search/tags?q=foo')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 4)
