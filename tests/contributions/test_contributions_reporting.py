import datetime
import csv
import StringIO

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import timezone

from bulbs.contributions.models import Contribution, ContributorRole

from tests.utils import BaseAPITestCase, make_content
from tests.testcontent.models import TestContentObj

from django.contrib.auth.models import User


class ContributionReportingTestCase(BaseAPITestCase):

    def setUp(self):
        super(ContributionReportingTestCase, self).setUp()
        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor"),
            "writer": ContributorRole.objects.create(name="Writer")
        }
        self.chris = User.objects.create(
            username="csinchok",
            first_name="Chris",
            last_name="Sinchok",
            is_staff=True)
        self.mike = User.objects.create(
            username="mwnuk",
            first_name="Mike",
            last_name="Wnuk",
            is_staff=True)

    def test_reporting_api(self):

        content_one = make_content(published=timezone.now() - datetime.timedelta(days=1))
        content_two = make_content(published=timezone.now() - datetime.timedelta(days=3))
        for content in content_one, content_two:
            Contribution.objects.create(
                content=content,
                contributor=self.chris,
                role=self.roles["editor"]
            )
            Contribution.objects.create(
                content=content,
                contributor=self.mike,
                role=self.roles["writer"]
            )

        client = Client()
        client.login(username="admin", password="secret")

        # Let's look at all the items
        endpoint = reverse("contributionreporting-list")
        start_date = timezone.now() - datetime.timedelta(days=4)
        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        # Now lets order by something else
        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d"), "ordering": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        # Now let's filter by date
        start_date = timezone.now() - datetime.timedelta(days=2)
        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Now let's check the CSV output
        start_date = timezone.now() - datetime.timedelta(days=4)
        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d"), "format": "csv"})
        self.assertEqual(response.status_code, 200)
        csvreader = csv.DictReader(StringIO.StringIO(response.content))
        self.assertEqual(len(csvreader.fieldnames), 12)
        for line in csvreader:
            pass
        self.assertEqual(csvreader.line_num, 5)  # Header + 4 items
