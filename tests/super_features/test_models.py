from django.db import IntegrityError

from rest_framework.serializers import ValidationError

from bulbs.super_features.models import ContentRelation, BaseSuperFeature, GUIDE_TO
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureModelTestCase(BaseIndexableTestCase):

    def test_create_success(self):
        sf = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )
        db_sf = BaseSuperFeature.objects.get(pk=sf.pk)
        self.assertEqual(db_sf.pk, sf.pk)

    def test_create_missing_field(self):
        with self.assertRaises(ValidationError):
            BaseSuperFeature.objects.create(
                title="Guide to Cats",
                notes="This is the guide to cats",
                superfeature_type=GUIDE_TO,
                data=[{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            )

    def test_create_parent_child(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": 1
            }
        )

        child = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        ContentRelation.objects.create(parent=parent, child=child, ordering=1)

        self.assertFalse(parent.is_child)
        self.assertTrue(child.is_child)

    def test_content_relation_uniqueness(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": 1
            }
        )

        child1 = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )
        child2 = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        ContentRelation.objects.create(parent=parent, child=child1, ordering=1)

        with self.assertRaises(IntegrityError):
            ContentRelation.objects.create(parent=parent, child=child2, ordering=1)
