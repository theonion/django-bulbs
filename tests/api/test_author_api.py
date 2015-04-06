from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test.client import Client

from bulbs.utils.test import BaseIndexableTestCase

# from django.conf import settings
# from django.db.models.loading import get_model
# User = get_model(*settings.AUTH_USER_MODEL.split("."))


class AuthorApiTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        User = get_user_model()
        super(AuthorApiTestCase, self).setUp()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_author_filter_detail(self):
        """Make sure author api works with BULBS_AUTHOR_FILTER values that
        could match the same user multiple times in a single queryset.
        """
        User = get_user_model()
        user = User.objects.create(
            username="Choo Choo The Herky-Jerky Dancer",
            first_name="Choo",
            last_name="Choo",
            is_staff=True
        )
        group_names = ("admin", "author")
        for name in group_names:
            group, _ = Group.objects.get_or_create(name=name)
            user.groups.add(group)

        with self.settings(BULBS_AUTHOR_FILTER={
            "groups__name__in": group_names
        }):
            client = Client()
            client.login(username="admin", password="secret")
            author_detail_endpoint = reverse("author-detail", kwargs=dict(pk=user.pk))
            response = client.get(author_detail_endpoint, content_type="application/json")
            self.assertTrue(response.status_code, 200)

    def test_author_search(self):
        User = get_user_model()

        test_names = (
            ("Chris", "Sinchok"),
            ("Adam", "Wentz"),
            ("Shawn", "Cook"),
            ("Andrew", "Kos"),
        )

        for first, last in test_names:
            User.objects.create(
                username=first.lower()[0] + last.lower(),
                first_name=first,
                last_name=last,
                is_staff=True
            )

        User.objects.create(
            username="ElDan",
            first_name="Some",
            last_name="Dude"
        )

        client = Client()
        client.login(username="admin", password="secret")

        author_endpoint = reverse("author-list")
        response = client.get(author_endpoint, content_type="application/json")
        self.assertEqual(len(response.data), 5)

        response = client.get(author_endpoint, {"search": "chris"}, content_type="application/json")
        self.assertEqual(len(response.data), 1)

        response = client.get(author_endpoint, {"search": "ok"}, content_type="application/json")
        self.assertEqual(len(response.data), 2)
