from django.core.exceptions import ValidationError as DBValidationError

from rest_framework.serializers import ValidationError

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureModelTestCase(BaseIndexableTestCase):

    def test_create_success(self):
        sf = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
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
                superfeature_type=GUIDE_TO_ENTRY,
                data=[{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            )

    def test_create_parent_child(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            default_child_type=GUIDE_TO_ENTRY,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        child = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        self.assertTrue(parent.is_parent)
        self.assertFalse(parent.is_child)
        self.assertTrue(child.is_child)
        self.assertFalse(child.is_parent)

    def test_content_relation_uniqueness(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        with self.assertRaises(DBValidationError):
            BaseSuperFeature.objects.create(
                title="Guide to Cats",
                notes="This is the guide to cats",
                superfeature_type=GUIDE_TO_ENTRY,
                parent=parent,
                ordering=1,
                data={
                    "entries": [{
                        "title": "Cats",
                        "copy": "Everybody loves cats"
                    }]
                }
            )

    def test_child_not_indexed(self):
        parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            default_child_type=GUIDE_TO_ENTRY,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        child = BaseSuperFeature.objects.create(
            title="Owning a cat",
            notes="this is a child page for the guide to cats feature",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        BaseSuperFeature.search_objects.refresh()
        results = self.es.search(
            BaseSuperFeature.search_objects.mapping.index,
            BaseSuperFeature.search_objects.mapping.doc_type
        )

        # check that child id is not in index
        self.assertEqual(results['hits']['total'], 1)
        self.assertTrue(child.id not in results['hits'])
