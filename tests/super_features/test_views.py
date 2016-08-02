from django.core.exceptions import ValidationError as DBValidationError

from rest_framework.serializers import ValidationError

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseIndexableTestCase


class SuperFeatureViewsTestCase(BaseIndexableTestCase):

    def test_super_feature_view(self):
        BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )
