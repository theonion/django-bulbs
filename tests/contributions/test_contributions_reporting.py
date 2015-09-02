import datetime
import csv

try:
    import StringIO
except ImportError:
    import io as StringIO

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import timezone
from django.contrib.auth.models import User

from bulbs.content.models import FeatureType
from bulbs.contributions.models import Contribution, ContributorRole
from bulbs.utils.test import BaseAPITestCase, make_content


class ContributionReportingTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionReportingTestCase, self).setUp()

        self.tvclub =  FeatureType.objects.create(name="TV Club")
        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor", payment_type=0),
            "writer": ContributorRole.objects.create(name="Writer", payment_type=1)
        }

        self.roles["editor"].flat_rates.create(rate=60)
        self.roles["writer"].feature_type_rates.create(feature_type=self.tvclub, rate=70)

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

        content_one = make_content(
            published=timezone.now() - datetime.timedelta(days=1),
            feature_type=self.tvclub
        )
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

        c1 = response.data[0]
        rate = c1.get("rate")
        self.assertEqual(rate, 60)

        c4 = response.data[3]
        rate = c4.get("rate")
        self.assertEqual(rate, 70)

        # Now lets order by something else
        response = client.get(endpoint,
                              data={"start": start_date.strftime("%Y-%m-%d"), "ordering": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        # Now let's filter by date
        start_date = timezone.now() - datetime.timedelta(days=2)
        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Now let's check the CSV output
        start_date = timezone.now() - datetime.timedelta(days=4)
        response = client.get(endpoint,
                              data={"start": start_date.strftime("%Y-%m-%d"), "format": "csv"})
        self.assertEqual(response.status_code, 200)
        csvreader = csv.DictReader(StringIO.StringIO(response.content.decode("utf8")))
        self.assertEqual(len(csvreader.fieldnames), 13)
        for line in csvreader:
            pass
        self.assertEqual(csvreader.line_num, 5)  # Header + 4 items

    def test_content_reporting(self):

        content_one = make_content(published=timezone.now() - datetime.timedelta(days=1))

        client = Client()
        client.login(username="admin", password="secret")

        # Let's look at all the items
        endpoint = reverse("contentreporting-list")
        start_date = timezone.now() - datetime.timedelta(days=4)

        content_one.authors.all().delete()

        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["editor"], "")
        self.assertEqual(response.data[0]["authors"], "")

        Contribution.objects.create(
            content=content_one,
            contributor=self.chris,
            role=self.roles["editor"]
        )
        Contribution.objects.create(
            content=content_one,
            contributor=self.mike,
            role=self.roles["editor"]
        )
        Contribution.objects.create(
            content=content_one,
            contributor=self.mike,
            role=self.roles["writer"]
        )

        self.jenny = User.objects.create(
            username="jcrowley",
            first_name="Jenny",
            last_name="Crowley",
            is_staff=True)

        content_one.authors.add(self.chris)
        content_one.authors.add(self.jenny)

        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["authors"], "Chris Sinchok,Jenny Crowley")

        self.assertEqual(response.data[0]["editor"], "Chris Sinchok,Mike Wnuk")
        self.assertEqual(response.data[0]["writer"], "Mike Wnuk")
