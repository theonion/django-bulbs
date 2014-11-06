import json
from elastimorphic.tests.base import BaseIndexableTestCase

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import Permission

from djbetty.fields import ImageFieldFile

from tests.testcontent.models import TestContentDetailImage
from tests.utils import JsonEncoder


# User = get_user_model()
# from django.conf import settings
# from django.db.models.loading import get_model
# User = get_model(*settings.AUTH_USER_MODEL.split("."))


class TestThumbnailing(BaseIndexableTestCase):
    """Test image/thumbnail fallbacks, etc"""

    def test_thumbnail_property(self):
        """Test that the thumbnail property works as intended."""

        content = TestContentDetailImage.objects.create(
            title="Test Content With Some Image",
            description="I wish these Image req's weren't so insane"
        )

        self.assertTrue(isinstance(content.thumbnail, ImageFieldFile))
        self.assertEqual(content.thumbnail.id, None)

        content.detail_image.id = 666
        self.assertEqual(content.thumbnail.id, 666)
        self.assertEqual(content.detail_image.id, 666)
        self.assertEqual(content.thumbnail_override.id, None)

        content.thumbnail_override = 6666
        self.assertEqual(content.thumbnail.id, 6666)
        self.assertEqual(content.detail_image.id, 666)
        self.assertEqual(content.thumbnail_override.id, 6666)

        # test that the thumbnail property is readonly
        with self.assertRaises(AttributeError):
            content.thumbnail = 6666

    def test_thumbail_override_api(self):
        """Test thumbnail override field can be used properly."""
        User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

        publish_perm = Permission.objects.get(codename="publish_content")
        change_perm = Permission.objects.get(codename="change_content")
        promote_perm = Permission.objects.get(codename="promote_content")
        admin.user_permissions.add(publish_perm, change_perm, promote_perm)

        client = Client()
        client.login(username="admin", password="secret")

        content = TestContentDetailImage.objects.create(
            title="Test Content With Some Image",
            foo="Fighters",
            description="I wish these Image req's weren't so insane",
            detail_image=666
        )

        content_detail_url = reverse("content-detail", kwargs={"pk": content.id})
        response = client.get(content_detail_url)
        self.assertEqual(response.status_code, 200)

        # Let's grab the data from the response
        content_data = response.data

        # Make sure the thumbnail is set, as it should be
        self.assertEqual(content_data["thumbnail"]["id"], 666)
        self.assertEqual(content_data["detail_image"]["id"], 666)

        # Hmmm, let's change the main image...
        content_data["detail_image"]["id"] = 1

        # Let's POST an update
        response = client.put(
            content_detail_url,
            data=json.dumps(content_data, cls=JsonEncoder),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Refresh the content object from the db
        content = TestContentDetailImage.objects.get(id=content.id)

        # Detail image should have an id of 1
        self.assertEqual(content.detail_image.id, 1)

        # The thumbnail property should return the new value
        self.assertEqual(content.thumbnail.id, 1)

        # The thumbnail override field should still be null, since we didn't *really* set it
        self.assertEqual(content.thumbnail_override.id, None)
