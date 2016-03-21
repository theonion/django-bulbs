from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.content.models import Content, Tag, FeatureType

from example.testcontent.models import TestRecircContentObject


class TestRecircMixins(BaseIndexableTestCase):

    def setUp(self):
        super(TestRecircMixins, self).setUp()

        self.ft = FeatureType.objects.create(name="Article")
        tag_names = (
            "Cool", "Funny", "Wow", "Amazings"
        )
        self.tags = []
        for name in tag_names:
            self.tags.append(Tag.objects.create(name=name))

        self.objects = []
        for tag in self.tags:
            t = TestRecircContentObject.objects.create(
                foo="foo",
                bar="bar",
                feature_type=self.ft
            )
            t.tags.add(tag)
            t.save()
            self.objects.append(t)

        self.objects[0].query = dict(
            included_ids=[self.objects[i].id for i in range(1, len(self.objects))]
        )
        self.objects[0].save()

        TestRecircContentObject.search_objects.refresh()

        self.assertEqual(self.objects[0].query, {
            "included_ids": [self.objects[i].id for i in range(1, len(self.objects))]
        })

    def test_query_clean(self):
        obj = self.objects[1]
        obj.query = dict(
            included_ids=[1, None]
        )
        obj.save_query()

        self.assertTrue(None not in obj.query)
        self.assertEqual(obj.query, {"included_ids": [1]})

    def test_query_get_content(self):
        obj = self.objects[0]
        count = obj.get_content().full().count()

        self.assertEqual(count, 0)

        # since the TestRecircContentObjects are not yet published
        count = obj.get_content(published=False).full().count()

        self.assertEqual(len(obj.query['included_ids']), count)
