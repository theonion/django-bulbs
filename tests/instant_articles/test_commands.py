from django.core.management import call_command

from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class MigrateIAFeatureTypeTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(MigrateIAFeatureTypeTestCase, self).setUp()
        self.featuretype = FeatureType.objects.create(name="News in Brief")
        self.non_ia_featuretype = FeatureType.objects.create(name="Blah Blah")
        make_content(
            TestContentObj,
            published=self.now,
            feature_type=self.featuretype,
            _quantity=50
        )

    def test_command(self):
        self.assertEqual(TestContentObj.search_objects.instant_articles().count(), 0)
        call_command("migrate_ia_featuretype", "--slug", self.featuretype.slug)
        TestContentObj.search_objects.refresh()
        self.assertEqual(TestContentObj.search_objects.instant_articles().count(), 50)
