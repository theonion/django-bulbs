import json

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone

from bulbs.special_coverage.models import SpecialCoverage
from tests.utils import BaseAPITestCase, make_content


class SpecialCoverageApiTestCase(BaseAPITestCase):

    def setUp(self):
        # set up client
        super(SpecialCoverageApiTestCase, self).setUp()

        # do client stuff
        self.client = Client()
        self.client.login(username="admin", password="secret")

        # set up a test special coverage
        self.special_coverage = SpecialCoverage.objects.create(
            name="Jackz Linkz Coveragez",
            slug="jackz-linkz-coveragez",
            description="Stuff about jerky.",
            query="",
            videos=""
        )

        self.special_coverage.save()

    def test_special_coverage_api(self):

        endpoint = reverse("special-coverage-list")
        print(endpoint)
        # endpoint = "/api/v1/special-coverage/"
        response = self.client.get(endpoint)

        print(response.data)



# TODO : test permissions for putting, posting, etc.
