import datetime
import csv

try:
    import StringIO
except ImportError:
    import io as StringIO

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import timezone
from django.contrib.auth.models import User

from bulbs.content.models import Content, FeatureType
from bulbs.contributions.models import (
    Contribution, ContributorRole, FreelanceProfile, HourlyRate,
    FeatureTypeRate, FeatureTypeOverride
)
from bulbs.utils.test import BaseIndexableTestCase, BaseAPITestCase, make_content


class ContributionReportingTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionReportingTestCase, self).setUp()

        self.tvclub = FeatureType.objects.create(name="TV Club")
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
        user_cls = get_user_model()
        admin = user_cls.objects.first()
        Contribution.objects.create(
            content=content_one,
            contributor=admin,
            role=self.roles['editor']
        )

        client = Client()
        client.login(username="admin", password="secret")

        # Let's look at all the items
        endpoint = reverse("contentreporting-list")
        start_date = timezone.now() - datetime.timedelta(days=4)

        content_one.authors.all().delete()

        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

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
        self.assertEqual(response.data[0]["value"], 180)

        self.assertEqual(response.data[0]["authors"], "Chris Sinchok,Jenny Crowley")

        # self.assertEqual(response.data[0]["editor"], "Chris Sinchok,Mike Wnuk")
        # self.assertEqual(response.data[0]["writer"], "Mike Wnuk")

    def test_freelance_reporting(self):
        client = Client()
        client.login(username="admin", password="secret")

        endpoint = reverse("freelancereporting-list")
        start_date = timezone.now() - datetime.timedelta(days=4)

        topdog = User.objects.create(
            username="topdog",
            first_name="Top",
            last_name="Dog",
            is_staff=True
        )
        FreelanceProfile.objects.create(contributor=topdog)

        otherdog = User.objects.create(
            username="otherdog",
            first_name="Other",
            last_name="Dog",
            is_staff=True
        )
        FreelanceProfile.objects.create(contributor=otherdog)

        content_one = make_content(published=timezone.now() - datetime.timedelta(days=1))

        Contribution.objects.create(
            content=content_one,
            contributor=topdog,
            role=self.roles["editor"]
        )
        Contribution.objects.create(
            content=content_one,
            contributor=otherdog,
            role=self.roles["editor"]
        )
        Contribution.objects.create(
            content=content_one,
            contributor=topdog,
            role=self.roles["writer"]
        )

        response = client.get(endpoint, data={"start": start_date.strftime("%Y-%m-%d")})
        self.assertEqual(response.status_code, 200)

    def test_feature_type_rate_override_dependency(self):
        FeatureTypeOverride.objects.delete()
        rate = FeatureTypeRate.objects.create(
            rate=60,
            role=self.roles["editor"],
            feature_type=self.tvclub
        )
        overrides = FeatureTypeOverride.objects.filter(
            role=rate.role,
            feature_type=rate.feature_type
        )
        self.assertEqual(overrides.count(), 1)

        override = overrides.first()
        self.assertEqual(override.role, rate.role)
        self.assertEqual(override.feature_type, rate.feature_type)

        rate.delete()
        overrides = FeatureTypeOverride.objects.all()
        self.assertEqual(overrides.count(), 0)


class RatePayTestCase(BaseIndexableTestCase):

    def setUp(self):
        contributor_cls = get_user_model()
        self.now = timezone.now()
        self.contributors = {
            'jarvis': contributor_cls.objects.create(
                first_name='jarvis',
                last_name='monster',
                username='garbage'
            )
        }
        self.roles = {
            'hourly': ContributorRole.objects.create(
                name='Hourly',
                payment_type=2
            )
        }
        self.rates = {
            'hourly': {
                'hourly': HourlyRate.objects.create(
                    role=self.roles['hourly'],
                    rate=70
                )
            }
        }
        self.content = {
            'c1': Content.objects.create(
                title='Good Content',
                published=self.now - timezone.timedelta(days=1)
            )
        }
        self.contributions = {
            'hourly': Contribution.objects.create(
                contributor=self.contributors['jarvis'],
                role=self.roles['hourly'],
                content=self.content['c1']
            )
        }

    def test_get_rate_hourly(self):
        contribution = self.contributions['hourly']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, HourlyRate)
        self.assertEqual(rate.rate, 70)
