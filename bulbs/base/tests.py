import rawes
import copy
import itertools
import datetime

from django.test import TestCase as DBTestCase
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone

from bulbs.base.models import Content
try:
    from testapp.models import TestContentObj, TestContentObjTwo
except:
    raise ImportError("Something with your test app isn't configured correctly")


class ESTestCase(DBTestCase):

    def setUp(self):
        # Create index, if necessary
        call_command('sync_es')
        self.es = rawes.Elastic(**settings.ES_SERVER)

    def tearDown(self):
        server_conf = copy.deepcopy(settings.ES_SERVER)
        index_name = server_conf['path']
        del server_conf['path']
        es = rawes.Elastic(**server_conf)
        es.delete(index_name)


class SearchTestCase(ESTestCase):

    def setUp(self):
        super(SearchTestCase, self).setUp()

        for tags in itertools.combinations(["tag1", "tag2", "tag3", "tag4"], 2):
            one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
            TestContentObj.objects.create(
                title="Tags: %s,%s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                tags=tags,
                published=one_hour_ago)

            TestContentObjTwo.objects.create(
                title="Tags: %s,%s" % (tags[0], tags[1]),
                field1=tags[0],
                field2=tags[1],
                field3=3,
                tags=tags,
                published=one_hour_ago)

        self.es.get('_refresh')

    def test_search(self):
        results = Content.objects.all()
        self.assertEqual(len(results), 12)

        results = Content.objects.search(content_type=["testapp.testcontentobjtwo", "testapp.testcontentobj"], tags=["tag1", "tag2"])
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertTrue('tag1' in result.tags)
            self.assertTrue('tag2' in result.tags)
            self.assertFalse('tag3' in result.tags)
            self.assertFalse('tag4' in result.tags)

        results = Content.objects.search(content_type=["testapp.testcontentobjtwo"])
        self.assertEqual(len(results), 6)

        results = Content.objects.search(content_type=["testapp.testcontentobj"])
        self.assertEqual(len(results), 6)
