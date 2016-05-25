from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient

from bulbs.utils.test import BaseAPITestCase

User = get_user_model()

TEST_EMAIL_TEMPLATE_PATH = "__bug_report_email.html"
TEST_EMAIL_TO_ADDRESSES = [
    "webtech@theonion.com",
    "bugs@theonion.net"
]
TEST_EMAIL_SUBJECT = "Hello from the CMS!"


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    BUG_REPORTER={
        "EMAIL_TEMPLATE_PATH": TEST_EMAIL_TEMPLATE_PATH,
        "EMAIL_TO_ADDRESSES": TEST_EMAIL_TO_ADDRESSES,
        "EMAIL_SUBJECT": TEST_EMAIL_SUBJECT
    }
)
class TestBugReportEmail(BaseAPITestCase):

    def post_mail(self, data=None):
        return self.client.post(
            reverse("report-bug"),
            data=data,
            format="json"
        )

    def create_mail(self, data=None):
        if data is None:
            data = self.test_data

        self.post_mail(data)

        return mail.outbox[0]

    def setUp(self):
        super(TestBugReportEmail, self).setUp()

        self.test_data = {
            "report": "My garbage report",
            "url": "www.theonion.com/my/garbage/article",
            "user_agent": "Firebox 2.0",
        }

        self.test_user = User.objects.create_user(
            "jbiden",
            "diamond.joe@comcast.net",
            "dj"
        )

        self.client = APIClient()
        self.client.login(username=self.test_user.username, password="dj")

    def test_email_body(self):
        """Test that an email is sent with all the info in the body."""

        email = self.create_mail()

        self.assertIn(self.test_data["report"], email.body)
        self.assertIn(self.test_data["url"], email.body)
        self.assertIn(self.test_data["user_agent"], email.body)

    def test_email_to_addresses(self):
        """Test that email is sent with the to addresses specified by settings."""

        email = self.create_mail()

        self.assertEqual(TEST_EMAIL_TO_ADDRESSES[0], email.to[0])
        self.assertEqual(TEST_EMAIL_TO_ADDRESSES[1], email.to[1])

    def test_email_from_address(self):
        """Test that the email is sent with the current user's email address."""

        email = self.create_mail()

        self.assertEqual(self.test_user.email, email.from_email)

    def test_email_subject(self):
        """Test that email is sent with the subject specified by settings."""

        email = self.create_mail()

        self.assertEqual(TEST_EMAIL_SUBJECT, email.subject)

    def test_name_last_and_first(self):
        """Test that user's full name is used if they have a first and last name
        set."""

        self.test_user.first_name = "Joe"
        self.test_user.last_name = "Biden"
        self.test_user.save()

        email = self.create_mail()

        self.assertIn(self.test_user.first_name, email.body)
        self.assertIn(self.test_user.last_name, email.body)

    def test_name_no_last_and_first(self):
        """Test that user's user name is used if they don't have a first and
        last name."""

        email = self.create_mail()

        self.assertIn(self.test_user.username, email.body)

    def test_http_response_200(self):
        """Test response that's sent back to client on a 200."""

        response = self.post_mail()

        self.assertEqual(response.status_code, HTTP_200_OK)
