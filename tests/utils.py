import json
from six import PY3
from elastimorphic.tests.base import BaseIndexableTestCase

# from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from django.conf import settings
from django.db.models.loading import get_model
User = get_model(*settings.AUTH_USER_MODEL.split("."))


class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if not PY3 and isinstance(value, str):
            return unicode(value, errors='replace')  # TODO: Be stricter.
        if isinstance(value, set):
            return list(value)
        return super(JsonEncoder, self).default(value)


def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if hasattr(value, 'strftime'):
        if hasattr(value, 'hour'):
            return value.isoformat()
        else:
            return '%sT00:00:00' % value.isoformat()


class BaseAPITestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        # User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()
        # reverse("content-detail")

    def give_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_content")
        change_perm = Permission.objects.get(codename="change_content")
        promote_perm = Permission.objects.get(codename="promote_content")
        self.admin.user_permissions.add(publish_perm, change_perm, promote_perm)

    def give_author_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_own_content")
        self.admin.user_permissions.add(publish_perm)

    def remove_permissions(self):
        self.admin.user_permissions.clear()
