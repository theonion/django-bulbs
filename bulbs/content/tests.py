import itertools
import datetime
import json

from elasticutils.contrib.django import get_es

from django.test import TestCase as DBTestCase
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from bulbs.content.models import Content, Tagish
try:
    from testapp.models import TestContentObj, TestContentObjTwo, Section
except:
    raise ImportError("Something with your test app isn't configured correctly")


class ESTestCase(DBTestCase):

    def setUp(self):
        # Create index, if necessary
        call_command('sync_es')
        self.es = get_es()
        self.es.refresh()

    def tearDown(self):
        self.es.delete_index(settings.ES_INDEXES.get('default'))


class ContentCreationTestCases(ESTestCase):

    def test_no_tags(self):
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        no_tags = TestContentObj.objects.create(
            title="No Tags",
            field1="No",
            field2="Tags",
            published=one_hour_ago)
        self.es.refresh()
        self.assertEqual(no_tags.tags.all(), [])
        no_tags.tags.add(["One tag", "Two tags", "Three tags"])
        self.es.refresh()
        self.assertEqual(len(no_tags.tags.all()), 3)


class ContentTestCase(ESTestCase):

    def setUp(self):
        super(ContentTestCase, self).setUp()

        for tags in itertools.combinations(["Tag 1", "Tag 2", "Tag 3", "Tag 4"], 2):
            one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
            obj = TestContentObj.objects.create(
                title="Tags: %s, %s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                feature_type="Testing Type",
                published=one_hour_ago)
            self.es.refresh()
            obj.tags.add(tags)

            obj2 = TestContentObjTwo.objects.create(
                title="Tags: %s, %s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                field3=3,
                published=one_hour_ago)
            self.es.refresh()
            obj2.tags.add(tags)

        self.es.refresh()

    def test_tag_content(self):
        tag = Tagish.from_name("Tag 1")
        self.assertEqual(tag.content().count(), 6)

    def test_facets(self):
        facet_counts = Content.search().facet('tags.slug').facet_counts()
        self.assertEqual(len(facet_counts['tags.slug']), 4)
        for facet in facet_counts['tags.slug']:
            self.assertEqual(facet['count'], 6)

    def test_content_search(self):
        results = Content.search()
        self.assertEqual(results.count(), 12)

        results = Content.search(query="Tag 1")
        self.assertEqual(results.count(), 6)

        results = Content.search(tags=["tag-1"])
        self.assertEqual(results.count(), 6)

        results = Content.search(tags=["tag-1", "tag-2"])
        self.assertEqual(results.count(), 2)
        for result in results:
            tags = result.tags.all()
            self.assertTrue(any(tag.slug == 'tag-1' for tag in tags))
            self.assertTrue(any(tag.slug == 'tag-2' for tag in tags))
            self.assertFalse(any(tag.slug == 'tag-3' for tag in tags))
            self.assertFalse(any(tag.slug == 'tag-4' for tag in tags))

        results = Content.search(types=[TestContentObjTwo])
        self.assertEqual(results.count(), 6)

        results = Content.search(types=[TestContentObj])
        self.assertEqual(len(results), 6)

        with self.assertRaises(AttributeError):
            results[0].feature_type = 'Some Feature Type'

        results = Tagish.search()
        self.assertEqual(results.count(), 4)

        results = Content.search(feature_types=["testing-type"])
        self.assertEqual(results.count(), 6)

        results = Content.search(feature_types=["overridden-feature-type"])
        self.assertEqual(results.count(), 6)

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

        self.tv_section = Section.objects.create(name="T.V.", description="The TV Section")
        self.es.refresh()  # It takes a few seconds for the indexing to propogate, unless we refresh.

    def test_tagish_objects(self):
        tv_section = Tagish.get("tv-section")
        self.assertEqual(tv_section.description, "The TV Section")
        self.assertEqual(tv_section.id, self.tv_section.id)

        new_tv_section = Section.objects.create(name="TV", description="Another TV Section")
        self.assertEqual(new_tv_section.slug, "tv-section-1")
        self.es.refresh()  # It takes a few seconds for the indexing to propogate, unless we refresh.
        self.assertEqual(Tagish.search().count(), 8)

    def test_tag_search(self):
        results = Tagish.search()
        self.assertEqual(results.count(), 7)

        results = Tagish.search('foo')
        self.assertEqual(results.count(), 2)

        results = Tagish.search('fooba')
        self.assertEqual(results.count(), 2)

    def test_tag_search_view(self):
        client = Client()
        response = client.get('/content/search/tags?q=foo')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(len(response_data), 2)
