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
        self.objects = []
        for i, tag in enumerate(self.tags):
            t = TestRecircContentObject.objects.create(
                title="Test {}".format(i + 1),
                foo="foo",
                bar="bar",
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(tag)
            self.objects.append(t)

        self.content = TestRecircContentObject.objects.create(
            foo="whatever",
            bar="who cares",
            feature_type=self.ft,
            published=timezone.now() - timezone.timedelta(days=1)
        )

        # set query in content object
        self.content.query = dict(
            included_ids=[
                o.id for o in TestRecircContentObject.objects.all().exclude(
                    id__in=[self.content.id]
                )
            ]
        )
        self.content.save()

    def test_recirc_url(self):
        # assert that there are more than 3 items in the response
        # & that the first three are as expected
        self.assertEqual(len(self.content.query['included_ids']), 4)
        self.assertEqual(self.content.query['included_ids'][0], self.objects[0].id)
        self.assertEqual(self.content.query['included_ids'][1], self.objects[1].id)
        self.assertEqual(self.content.query['included_ids'][2], self.objects[2].id)

        # refresh search objects
        TestRecircContentObject.search_objects.refresh()

        # call endpoint w/ content id
        recirc_url = reverse('content_recirc', kwargs={'pk': self.content.id})
        response = self.client.get(recirc_url)
        data = json.loads(json.dumps(response.data))

        self.assertEqual(response.status_code, 200)

        # assert first three things are returned from endpoint
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['id'], self.objects[2].id)
        self.assertEqual(data[0]['thumbnail'], None)
        self.assertEqual(data[0]['slug'], 'test-3')
        self.assertEqual(data[0]['title'], 'Test 3')
        self.assertEqual(data[0]['feature_type'], 'Article')

        self.assertEqual(data[1]['id'], self.objects[1].id)
        self.assertEqual(data[1]['thumbnail'], None)
        self.assertEqual(data[1]['slug'], 'test-2')
        self.assertEqual(data[1]['title'], 'Test 2')
        self.assertEqual(data[1]['feature_type'], 'Article')

        self.assertEqual(data[2]['id'], self.objects[0].id)
        self.assertEqual(data[2]['thumbnail'], None)
        self.assertEqual(data[2]['slug'], 'test-1')
        self.assertEqual(data[2]['title'], 'Test 1')
        self.assertEqual(data[2]['feature_type'], 'Article')

        # assert that the query wasn't changed
        self.assertEqual(len(self.content.query['included_ids']), 4)
        self.assertEqual(self.content.query['included_ids'][0], self.objects[0].id)
        self.assertEqual(self.content.query['included_ids'][1], self.objects[1].id)
        self.assertEqual(self.content.query['included_ids'][2], self.objects[2].id)
        self.assertEqual(self.content.query['included_ids'][3], self.objects[3].id)

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

    def test_recirc_tag_fallback(self):
        # create test articles w/ matching tag
        tag = Tag.objects.create(name="Politics")
        for i in range(5):
            t = TestRecircContentObject.objects.create(
                title="{}".format(i),
                foo="{}".format(i),
                bar="{}".format(i),
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(tag)
            t.save()

        # create test articles w/ not matching tag
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
        content.query = dict(
            included_ids=[]
        )
        content.save()

        # refresh search objects
        TestRecircContentObject.search_objects.refresh()

        recirc_url = reverse('content_recirc', kwargs={'pk': content.id})
        response = self.client.get(recirc_url)
        data = json.loads(json.dumps(response.data))

        # assert that 3 items are returned & they are all of the correct type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertTrue(data[0]['title'].isdigit())
        self.assertTrue(data[0]['feature_type'], 'Article')
        self.assertTrue(data[1]['title'].isdigit())
        self.assertTrue(data[1]['feature_type'], 'Article')
        self.assertTrue(data[2]['title'].isdigit())
        self.assertTrue(data[2]['feature_type'], 'Article')

    def test_inline_recirc_url(self):
        # create test articles w/ matching tag
        tag = Tag.objects.create(name="Politics")
        for i in range(5):
            t = TestRecircContentObject.objects.create(
                title="{}".format(i),
                foo="{}".format(i),
                bar="{}".format(i),
                feature_type=self.ft,
                published=timezone.now() - timezone.timedelta(days=1)
            )
            t.tags.add(tag)
            t.save()

        # create test articles w/ not matching tag
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
        data = json.loads(json.dumps(response.data))

        # assert that 3 items are returned & they are all of the correct type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertTrue(data[0]['title'].isdigit())
        self.assertTrue(data[0]['feature_type'], 'Article')
        self.assertTrue(data[1]['title'].isdigit())
        self.assertTrue(data[1]['feature_type'], 'Article')
        self.assertTrue(data[2]['title'].isdigit())
        self.assertTrue(data[2]['feature_type'], 'Article')
