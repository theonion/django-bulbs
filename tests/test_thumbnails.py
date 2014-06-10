from elastimorphic.tests.base import BaseIndexableTestCase

from djbetty.fields import ImageFieldFile

from tests.testcontent.models import TestContentDetailImage


class TestThumbnailing(BaseIndexableTestCase):
    """Test image/thumbnail fallbacks, etc"""

    def test_thumbnail_property(self):

        content = TestContentDetailImage.objects.create(
            title="Test Content With Some Image",
            description="I wish these Image req's weren't so insane"
        )

        self.assertTrue(isinstance(content.thumbnail, ImageFieldFile))
        self.assertEqual(content.thumbnail.id, None)

        content.detail_image.id = 666
        self.assertEqual(content.thumbnail.id, 666)
        self.assertEqual(content.detail_image.id, 666)
        self.assertEqual(content._thumbnail.id, None)

        content.thumbnail = 6666
        self.assertEqual(content.thumbnail.id, 6666)
        self.assertEqual(content.detail_image.id, 666)
        self.assertEqual(content._thumbnail.id, 6666)
