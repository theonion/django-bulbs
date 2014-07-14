from __future__ import absolute_import

import datetime

from django.utils import timezone

from bulbs.content.models import Content, Tag, FeatureType
from bulbs.content.serializers import ContentSerializer
from tests.testcontent.models import TestContentObj
from elastimorphic.tests.base import BaseIndexableTestCase


class SerializerTestCase(BaseIndexableTestCase):

    def test_tag_serializer(self):
        # generate some data
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        some_bullshit = FeatureType.objects.create(name="Some Bullshit", slug="some-bullshit")
        test_obj = TestContentObj(
            title='Testing Tag Serialization',
            description='Serialization shouldn\'t be so hard',
            published=one_hour_ago,
            feature_type=some_bullshit,
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

    def test_deserialize_none(self):
        s = Content.get_serializer_class()(data=None)
        s.data
