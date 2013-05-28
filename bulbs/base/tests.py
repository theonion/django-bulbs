import itertools
import datetime

from elasticutils import get_es, S

from django.test import TestCase as DBTestCase
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone

from bulbs.base.models import Contentish
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


class SearchTestCase(ESTestCase):

    def setUp(self):
        super(SearchTestCase, self).setUp()

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

    def test_search(self):
        results = Contentish.search()
        self.assertEqual(results.count(), 12)

        results = Contentish.search(tags=["tag-1"])
        self.assertEqual(len(results), 6)

        results = Contentish.search(tags=["tag-1", "tag-2"])
        self.assertEqual(len(results), 2)
        # for result in results:
        #     self.assertTrue('tag1' in result.tags)
        #     self.assertTrue('tag2' in result.tags)
        #     self.assertFalse('tag3' in result.tags)
        #     self.assertFalse('tag4' in result.tags)

        results = Contentish.search(types=[TestContentObjTwo])
        self.assertEqual(len(results), 6)

        results = Contentish.search(types=[TestContentObj])
        self.assertEqual(len(results), 6)

        # results = Content.objects.search(content_type=["testapp.testcontentobj"])
        # self.assertEqual(len(results), 6)
