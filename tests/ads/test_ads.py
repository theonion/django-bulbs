from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.http import urlencode

from bulbs.utils.test import BaseAPITestCase


# TODO: factor out the user+permission stuff from ContentAPITestCase
class TestTargetingView(BaseAPITestCase):

    def test_get_fail(self):
        client = Client()
        nothing = client.get(reverse("targeting"))
        # you don't even get nothing without permission
        self.assertEqual(nothing.status_code, 403)
        # ok, have nothing, if that's your thing.
        client.login(username="admin", password="secret")
        self.give_permissions()
        nothing = client.get(reverse("targeting"))
        self.assertEqual(nothing.status_code, 404)

        param = urlencode({"url": "some/bull/shit"})
        url = "{0}?{1}".format(reverse("targeting"), param)
        also_nothing = client.get(url)
        self.assertEqual(also_nothing.status_code, 404)

    def give_permissions(self):
        target_perm = Permission.objects.get(codename="change_targetingoverride")
        self.admin.user_permissions.add(target_perm)

    # Don't like these tests because they're dependant on the feature-jump view
    # Tapping out on this one

    # def test_get_success(self):
    #     client = Client()
    #     param = urlencode({"url": reverse("feature-jump")})
    #     url = "{0}?{1}".format(reverse("targeting"), param)
    #     targeting = client.get(url)
    #     self.assertEqual(targeting.status_code, 200)

    # def test_post(self):
    #     client = Client()
    #     param = urlencode({"url": reverse("feature-jump")})
    #     url = "{0}?{1}".format(reverse("targeting"), param)
    #     data = {
    #         "dfp_caneatme": "dickpills"
    #     }
    #     targeting = client.post(url, data=data)
    #     self.assertEqual(targeting.status_code, 3490234)
