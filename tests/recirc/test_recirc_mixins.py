from django.utils import timezone

from bulbs.utils.test import BaseIndexableTestCase
from bulbs.content.models import Content, Tag

from example.testcontent.models import TestRecircContentObject


class TestRericMixins(BaseIndexableTestCase):

    def setUp(self):
        super(TestRericMixins, self).setUp()

        tag_names = (
            "Cool", "Funny", "Wow", "Amazings"
        )
        self.tags = []
        for name in tag_names:
            self.tags.append(Tag.objects.create(name=name))

    def test_mixin_query_creation(self):
        objects = []
        for tag in self.tags:
            t = TestRecircContentObject.objects.create(
                foo="foo",
                bar="bar"
            )
            t.tags.add(tag)
            t.save()
            objects.append(t)

        objects[0].query = dict(
            included_ids=[objects[i].id for i in range(1, len(objects))]
        )
        objects[0].save()

        self.assertEqual(objects[0].query, {
            "included_ids": [objects[i].id for i in range(1, len(objects))]
        })
