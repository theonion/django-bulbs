from bulbs.content.models import FeatureType
from bulbs.utils.test import make_content, BaseIndexableTestCase

from example.testcontent.models import TestContentObj


class BaseIndexableFeatureTypeTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(BaseIndexableFeatureTypeTestCase, self).setUp()
        self.featuretype = FeatureType.objects.create(name="News in Brief")
        # Published Instant Articles
        make_content(
            TestContentObj,
            published=self.now,
            feature_type=self.featuretype,
            _quantity=50
        )
        # Unpublished Instant Articles
        make_content(
            TestContentObj,
            feature_type=self.featuretype,
            _quantity=50
        )


class FeatureTypeModelTestCase(BaseIndexableFeatureTypeTestCase):

    def test_db_instant_article(self):
        self.assertFalse(self.featuretype.instant_article)
        self.assertFalse(self.featuretype._db_instant_article)
        self.assertFalse(self.featuretype.instant_article_is_dirty)

        # Update FeatureType state.
        self.featuretype.instant_article = True
        self.assertTrue(self.featuretype.instant_article)
        self.assertFalse(self.featuretype._db_instant_article)
        self.assertTrue(self.featuretype.instant_article_is_dirty)

        # Save to database
        self.featuretype.save()
        self.assertTrue(self.featuretype.instant_article)
        self.assertTrue(self.featuretype._db_instant_article)
        self.assertFalse(self.featuretype.instant_article_is_dirty)

    def test_feature_type_instant_index(self):
        obj = TestContentObj.objects.first()
        doc = obj.to_dict()
        self.assertFalse(doc["feature_type"]["instant_article"])
        self.assertEqual(
            TestContentObj.search_objects.instant_articles().count(),
            0
        )

        # Update featuretype
        self.featuretype.instant_article = True
        self.featuretype.save()

        TestContentObj.search_objects.refresh()
        obj = TestContentObj.objects.first()
        doc = obj.to_dict()
        self.assertTrue(doc["feature_type"]["instant_article"])
        self.assertEqual(
            TestContentObj.search_objects.instant_articles().count(),
            50
        )

    def test_is_new(self):
        new_feature_type = FeatureType(name='New Feature Type', slug='new-feature-type')
        existing_feature_type = FeatureType.objects.create(
            name='Existing Feature Type',
            slug='existing-feature-type')

        self.assertTrue(new_feature_type.is_new())
        self.assertFalse(existing_feature_type.is_new())
