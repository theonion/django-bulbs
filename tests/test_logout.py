from django.core.urlresolvers import reverse
from django.test import Client
from elastimorphic.tests.base import BaseIndexableTestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class TestLogoutApi(BaseIndexableTestCase):
    """Test logout API endpoint."""

    def test_logout(self):

        # create and get a test user
        user = User.objects.create_user('onions', 'wh@tever.com', 'password')
        user.is_staff = True
        user.save()

        # log user in
        client = Client()
        logged_in = client.login(username='onions', password='password')
        self.assertTrue(logged_in)

        # check that user is logged in
        self.assertTrue(client.session['_auth_user_id'], user.pk)

        print client.session['_auth_user_id']

        # log user out via endpoint
        request = client.get(
            reverse('logout')
        )

        # check that user is logged out
        self.assertEqual(request.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
