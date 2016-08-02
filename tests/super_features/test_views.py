from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureViewsTestCase(BaseIndexableTestCase):

    def set_up(self):
        parent = BaseSuperFeature.objects.create(
            title="A Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        BaseSuperFeature.objects.create(
            title="Cats are cool",
            notes="Child page 1",
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
        BaseSuperFeature.objects.create(
            title="Cats are neat",
            notes="Child page 2",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=parent,
            ordering=2,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        parent2 = BaseSuperFeature.objects.create(
            title="ZZZZZZZ",
            notes="what",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )

    def test_super_feature_view(self):
        # hit list endpoint
        # check that only parents are in there


        # test search filter

        # test ordering
