import sys

if sys.version_info.major >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from bulbs.utils.test import BaseIndexableTestCase


User = get_user_model()


class TokenAuthTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(TokenAuthTestCase, self).setUp()
        self.client = APIClient()
        self.admin = User.objects.create(username="admin", password="secret")
        self.admin.is_staff = True
        self.admin.save()

    def test_auth_token_api(self):
        token = Token.objects.create(user=self.admin)
        content_endpoint = reverse('content-list')
        auth = 'Token ' + str(token)
        resp = self.client.get(content_endpoint, HTTP_AUTHORIZATION=auth)
        self.assertEqual(resp.status_code, 200)

    def test_auth_token_from_command(self):
        content_endpoint = reverse('content-list')
        stdout = StringIO()
        call_command("create_app_authtoken", '--username', 'admin', stdout=stdout)
        stdout.seek(0)
        auth = 'Token ' + str(stdout.read()).rstrip('\n')
        resp = self.client.get(content_endpoint, HTTP_AUTHORIZATION=auth)
        self.assertEqual(resp.status_code, 200)

    def test_auth_token_from_command_new_user(self):
        content_endpoint = reverse('content-list')
        stdout = StringIO()
        call_command("create_app_authtoken", '--username', 'combine', stdout=stdout)
        stdout.seek(0)
        auth = 'Token ' + str(stdout.read()).rstrip('\n')
        resp = self.client.get(content_endpoint, HTTP_AUTHORIZATION=auth)
        self.assertEqual(resp.status_code, 200)

    def test_auth_no_permissions(self):
        User.objects.create(username='bigjerk')
        content_endpoint = reverse('content-list')
        stdout = StringIO()
        call_command("create_app_authtoken", '--username', 'bigjerk', stdout=stdout)
        stdout.seek(0)
        auth = 'Token ' + str(stdout.read()).rstrip('\n')
        resp = self.client.get(content_endpoint, HTTP_AUTHORIZATION=auth)
        self.assertEqual(resp.status_code, 403)
