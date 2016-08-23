from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.utils import timezone

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

    def test_parent_set_child_dates(self):
        url = reverse('super-feature-set-children-dates',  kwargs={'pk': self.parent.pk})
        resp = self.api_client.post(url)

        # Will be 400 since parent publish date is not set
        self.assertEqual(resp.status_code, 400)

        self.parent.published = timezone.now()
        self.parent.save()

        url = reverse('super-feature-set-children-dates',  kwargs={'pk': self.parent.pk})
        resp = self.api_client.post(url)

        # Will be 200 since parent publish date is now set
        self.assertEqual(resp.status_code, 200)

        child = BaseSuperFeature.objects.get(id=self.child.id)
        self.assertEqual(self.parent.published, child.published)
