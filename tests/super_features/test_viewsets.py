from collections import OrderedDict

from django.core.urlresolvers import reverse

from bulbs.super_features.models import (
    BaseSuperFeature, GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
)
from bulbs.utils.test import BaseAPITestCase


class SuperFeatureViewsetsTestCase(BaseAPITestCase):

    def setUp(self):
        super(SuperFeatureViewsetsTestCase, self).setUp()
        self.parent = BaseSuperFeature.objects.create(
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
            parent=self.parent,
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
            parent=self.parent,
            ordering=2,
            data={
                "entries": [{
                    "title": "Cats",
                    "copy": "Everybody loves cats"
                }]
            }
        )

        self.parent2 = BaseSuperFeature.objects.create(
            title="ZZZZZZZ",
            notes="what",
            superfeature_type=GUIDE_TO_HOMEPAGE,
            data={
                "sponsor_text": "Fancy Feast",
                "sponsor_image": {"id": 1}
            }
        )
        self.list_url = reverse('super-feature-list')

    def test_super_feature_listing(self):
        response = self.api_client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        # assert children don't show
        self.assertTrue("Cats are cool" not in response.data['results'])
        self.assertTrue("Cats are neat" not in response.data['results'])

    def test_super_feature_listing_ordering(self):
        ordering_url = self.list_url + "?ordering=title"
        response = self.api_client.get(ordering_url)

        self.assertEqual(response.data['results'][0]['title'], self.parent.title)
        self.assertEqual(response.data['results'][1]['title'], self.parent2.title)

        ordering_url = self.list_url + "?ordering=-title"
        response = self.api_client.get(ordering_url)

        self.assertEqual(response.data['results'][0]['title'], self.parent2.title)
        self.assertEqual(response.data['results'][1]['title'], self.parent.title)

    def test_super_feature_listing_search(self):
        ordering_url = self.list_url + "?search=A Guide"
        response = self.api_client.get(ordering_url)

        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.parent.title)
