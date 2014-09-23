from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client

from elastimorphic.tests.base import BaseIndexableTestCase

User = get_user_model()


class AuthorApiTestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(AuthorApiTestCase, self).setUp()
        admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()

    def test_author_search(self):

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
