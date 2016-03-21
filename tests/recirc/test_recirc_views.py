from django.core.urlresolvers import reverse

from bulbs.content.models import Tag, FeatureType
from bulbs.utils.test import BaseAPITestCase

from example.testcontent.models import TestRecircContentObject


class TestRecircViews(BaseAPITestCase):

    def setUp(self):
        super(TestRecircViews, self).setUp()

        self.ft = FeatureType.objects.create(name="Article")
        tag_names = (
            "Cool", "Funny", "Wow", "Amazings"
        )
        self.tags = []
        for name in tag_names:
            self.tags.append(Tag.objects.create(name=name))

    def test_recirc_url(self):
        # create dumb test objects
        objects = []
        for tag in self.tags:
            t = TestRecircContentObject.objects.create(
                foo="foo",
                bar="bar",
                feature_type=self.ft
            )
            t.tags.add(tag)
            objects.append(t)

        content = TestRecircContentObject.objects.create(
            foo="whatever",
            bar="who cares",
            feature_type=self.ft
        )

        # set query in content object
        content.query = dict(
            included_ids=[
                o.id for o in TestRecircContentObject.objects.all().exclude(id__in=[content.id])
            ]
        )
        content.save()

        # refresh search objects
        TestRecircContentObject.search_objects.refresh()

        import pdb; pdb.set_trace()

        # call endpoint
        recirc_url = reverse('content_recirc', kwargs={'pk': 1})
        response = self.api_client.get(recirc_url)
        self.assertEqual(response.status_code, 200)

        # assert first three things are returned from dumb endpoint

    def test_recirc_content_not_found(self):
        pass

    def test_recirc_unpublished(self):
        pass
