from __future__ import absolute_import

import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone

from bulbs.content.models import Tag, FeatureType
from bulbs.content.serializers import ContentSerializer


from example.testcontent.models import TestContentObj
from bulbs.utils.test import BaseIndexableTestCase


class SerializerTestCase(BaseIndexableTestCase):

    def test_content_serializer(self):
        data = {
            "title": "testing"
        }
        serializer = ContentSerializer(data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.id > 0
        assert content.title == "testing"

    def test_feature_type_field(self):
        # Make sure we can create new Feature Types by just posting in a name
        data = {
            "title": "testing",
            "feature_type": "Clickventure"
        }
        serializer = ContentSerializer(data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.id > 0
        assert content.feature_type.name == "Clickventure"
        assert FeatureType.objects.count() == 1

        ft = FeatureType.objects.get(name="Clickventure")
        data = {
            "title": "testing",
            "feature_type": {"id": ft.id, "name": "Poopventure", "slug": "poopventure"}
        }
        serializer = ContentSerializer(data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.id > 0
        assert content.feature_type.name == "Clickventure"
        assert FeatureType.objects.count() == 1
        assert FeatureType.objects.get().name == "Clickventure"

        data["feature_type"] = None
        # Now remove the author
        serializer = ContentSerializer(content, data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.feature_type is None

    def test_author_field(self):
        author = get_user_model().objects.create(username="some-author")
        data = {
            "title": "testing",
            "authors": [{"id": author.id}]
        }
        serializer = ContentSerializer(data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.id > 0
        assert content.authors.count() == 1

        data["authors"] = []
        # Now remove the author
        serializer = ContentSerializer(content, data=data)
        serializer.is_valid()
        content = serializer.save()
        assert content.authors.count() == 0

    def test_tag_field(self):
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
