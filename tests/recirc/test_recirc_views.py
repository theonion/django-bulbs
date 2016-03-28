from django.core.urlresolvers import reverse
from django.utils import timezone

import json

from bulbs.content.models import Tag, FeatureType
from bulbs.utils.test import BaseIndexableTestCase

from example.testcontent.models import TestRecircContentObject


class TestRecircViews(BaseIndexableTestCase):

    def setUp(self):
        super(TestRecircViews, self).setUp()

        self.ft = FeatureType.objects.create(name="Article")
        tag_names = (
            "Cool", "Funny", "Wow", "Amazing"
        )
        self.tags = []
        for name in tag_names:
            self.tags.append(Tag.objects.create(name=name))

        # create dumb test objects
        objects = []
        for i, tag in enumerate(self.tags):
            t = TestRecircContentObject.objects.create(
                title="Test {}".format(i+1),
                foo="foo",
                bar="bar",
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(tag)
            objects.append(t)

        self.content = TestRecircContentObject.objects.create(
            foo="whatever",
            bar="who cares",
            feature_type=self.ft,
            published=timezone.now() - timezone.timedelta(days=1)
        )

        # set query in content object
        self.content.query = dict(
            included_ids=[
                o.id for o in TestRecircContentObject.objects.all().exclude(id__in=[self.content.id])
            ]
        )
        self.content.save()

    def tearDown(self):
        super(TestRecircViews, self).tearDown()

        TestRecircContentObject.objects.all().delete()
        TestRecircContentObject.search_objects.refresh()

    def test_recirc_url(self):
        # assert that there are more than 3 items in the response
        # & that the first three are as expected
        self.assertEqual(len(self.content.query['included_ids']), 4)
        self.assertEqual(self.content.query['included_ids'][0], 1)
        self.assertEqual(self.content.query['included_ids'][1], 2)
        self.assertEqual(self.content.query['included_ids'][2], 3)

        # refresh search objects
        TestRecircContentObject.search_objects.refresh()

        # call endpoint w/ content id
        recirc_url = reverse('content_recirc', kwargs={'pk': self.content.id})
        response = self.client.get(recirc_url)
        data = json.loads(json.dumps(response.data))

        self.assertEqual(response.status_code, 200)

        # assert first three things are returned from endpoint
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['id'], 3)
        self.assertEqual(data[0]['thumbnail'], None)
        self.assertEqual(data[0]['slug'], 'test-3')
        self.assertEqual(data[0]['title'], 'Test 3')
        self.assertEqual(data[0]['feature_type'], 'Article')

        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['thumbnail'], None)
        self.assertEqual(data[1]['slug'], 'test-2')
        self.assertEqual(data[1]['title'], 'Test 2')
        self.assertEqual(data[1]['feature_type'], 'Article')

        self.assertEqual(data[2]['id'], 1)
        self.assertEqual(data[2]['thumbnail'], None)
        self.assertEqual(data[2]['slug'], 'test-1')
        self.assertEqual(data[2]['title'], 'Test 1')
        self.assertEqual(data[2]['feature_type'], 'Article')

        # assert that the query wasn't changed
        self.assertEqual(len(self.content.query['included_ids']), 4)
        self.assertEqual(self.content.query['included_ids'][0], 1)
        self.assertEqual(self.content.query['included_ids'][1], 2)
        self.assertEqual(self.content.query['included_ids'][2], 3)
        self.assertEqual(self.content.query['included_ids'][3], 4)

    def test_recirc_content_not_found(self):
        recirc_url = reverse('content_recirc', kwargs={'pk': 300})
        response = self.client.get(recirc_url)
        self.assertEqual(response.status_code, 404)

    def test_recirc_unpublished(self):
        content = TestRecircContentObject.objects.create(
            foo="whatever",
            bar="who cares",
            feature_type=self.ft,
            published=timezone.now() + timezone.timedelta(days=1)
        )

        recirc_url = reverse('content_recirc', kwargs={'pk': content.id})
        response = self.client.get(recirc_url)
        self.assertEqual(response.status_code, 404)

    def test_inline_recirc_url(self):
        # create test articles w/ another tag
        tag = Tag.objects.create(name="Politics")
        for i in range(5):
            t = TestRecircContentObject.objects.create(
                title="{}".format(i+1),
                foo="{}".format(i+1),
                bar="{}".format(i+1),
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(tag)
            t.save()

        # create test articles w/ 1 tag
        exclude = Tag.objects.create(name="Music")
        for i in range(5):
            t = TestRecircContentObject.objects.create(
                title="EXCLUDE",
                foo="WHATEVER",
                bar="MAN",
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(exclude)
            t.save()

        # create master content article to test against
        content = TestRecircContentObject.objects.create(
            title="Master object",
            foo="foo",
            bar="bar",
            feature_type=self.ft,
            published=timezone.now() - timezone.timedelta(days=1)
        )
        content.tags.add(tag)

        # refresh search objects
        TestRecircContentObject.search_objects.refresh()

        # check that they are returned in the response
        recirc_url = reverse('content_inline_recirc', kwargs={'pk': content.id})
        response = self.client.get(recirc_url)
        self.assertEqual(response.status_code, 200)

        import pdb; pdb.set_trace()
