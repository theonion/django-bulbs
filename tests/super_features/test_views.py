from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseAPITestCase


class SuperFeatureViewsTestCase(BaseAPITestCase):

    def setUp(self):
        super(SuperFeatureViewsTestCase, self).setUp()
        self.parent = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        self.child = BaseSuperFeature.objects.create(
            title="Guide to Cats",
            notes="This is the guide to cats",
            superfeature_type=GUIDE_TO_ENTRY,
            parent=self.parent,
            ordering=1,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

    def test_parent_get_children(self):
        url = reverse('super-feature-relations', kwargs={'pk': self.parent.pk})
        resp = self.api_client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [
            OrderedDict([
                ('id', self.child.id),
                ('internal_name', None),
                ('title', 'Guide to Cats')
            ])
        ])
