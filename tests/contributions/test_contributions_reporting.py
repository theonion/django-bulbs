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
    Contribution, ContributionOverride, ContributorRole, FreelanceProfile,
    FlatRate, FeatureTypeRate, FeatureTypeOverride, HourlyRate, ManualRate,
    FeatureTypeOverrideProfile, Override
)
from bulbs.contributions.utils import get_forced_payment_contributions
from bulbs.utils.test import (
    BaseIndexableTestCase, BaseAPITestCase, make_content
)


class ContributionReportingTestCase(BaseAPITestCase):
    def setUp(self):
        super(ContributionReportingTestCase, self).setUp()
        self.tvclub = FeatureType.objects.create(name="TV Club")
        self.roles = {
            "editor": ContributorRole.objects.create(name="Editor", payment_type=0),
            "writer": ContributorRole.objects.create(name="Writer", payment_type=1)
        }

        self.roles["editor"].flat_rates.create(rate=60)
        rate = self.roles["writer"].feature_type_rates.get(feature_type=self.tvclub)
        rate.rate = 70
        rate.save()

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

    def test_feature_type_rate_on_save(self):
        role = ContributorRole.objects.create(name='Feature Type Guy', payment_type=1)
        self.assertEqual(role.feature_type_rates.count(), 1)

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
        self.assertEqual(len(csvreader.fieldnames), 14)
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


class RatePayTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(RatePayTestCase, self).setUp()
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
            'featuretype': ContributorRole.objects.create(
                name='FeatureType',
                payment_type=1
            ),
            'flatrate': ContributorRole.objects.create(
                name='FlatRate',
                payment_type=0
            ),
            'hourly': ContributorRole.objects.create(
                name='Hourly',
                payment_type=2
            ),
            'manual': ContributorRole.objects.create(
                name='Manual',
                payment_type=3
            )
        }
        self.feature_types = {
            'tvclub': FeatureType.objects.create(name='TV Club'),
            'news': FeatureType.objects.create(name='News')
        }
        self.rates = {
            'featuretype': {
                'tvclub': FeatureTypeRate.objects.create(
                    feature_type=self.feature_types['tvclub'],
                    role=self.roles['featuretype'],
                    rate=30
                ),
                'news': FeatureTypeRate.objects.create(
                    feature_type=self.feature_types['news'],
                    role=self.roles['featuretype'],
                    rate=50
                )
            },
            'flatrate': {
                'flatrate': FlatRate.objects.create(
                    role=self.roles['flatrate'],
                    rate=200
                )
            },
            'hourly': {
                'hourly': HourlyRate.objects.create(
                    role=self.roles['hourly'],
                    rate=60
                )
            },
        }
        self.content = {
            'c1': Content.objects.create(
                title='Good Content',
                feature_type=self.feature_types['tvclub'],
                published=self.now - timezone.timedelta(days=1)
            ),
            'c2': Content.objects.create(
                title='More Content',
                feature_type=self.feature_types['news'],
                published=self.now - timezone.timedelta(days=2)
            )
        }
        self.contributions = {
            'featuretype': {
                'tvclub': Contribution.objects.create(
                    contributor=self.contributors['jarvis'],
                    role=self.roles['featuretype'],
                    content=self.content['c1']
                ),
                'news': Contribution.objects.create(
                    contributor=self.contributors['jarvis'],
                    role=self.roles['featuretype'],
                    content=self.content['c2']
                )
            },
            'flatrate': Contribution.objects.create(
                contributor=self.contributors['jarvis'],
                role=self.roles['flatrate'],
                content=self.content['c1']
            ),
            'hourly': Contribution.objects.create(
                contributor=self.contributors['jarvis'],
                minutes_worked=30,
                role=self.roles['hourly'],
                content=self.content['c1']
            ),
            'manual': Contribution.objects.create(
                contributor=self.contributors['jarvis'],
                role=self.roles['manual'],
                content=self.content['c1']
            )
        }
        self.rates['manual'] = {
            'manual': ManualRate.objects.create(
                contribution=self.contributions['manual'],
                rate=1000
            )
        }

    def test_get_rate_flat_rate(self):
        contribution = self.contributions['flatrate']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, FlatRate)
        self.assertEqual(rate.rate, 200)

    def test_get_pay_flat_rate(self):
        contribution = self.contributions['flatrate']
        self.assertEqual(contribution.get_pay, 200)

    def test_get_override_flat_rate(self):
        Override.objects.create(
            contributor=self.contributors['jarvis'],
            role=self.roles['flatrate'],
            rate=80
        )
        contribution = self.contributions['flatrate']
        self.assertEqual(contribution.get_override, 80)
        self.assertEqual(contribution.get_pay, 80)

    def test_get_contribution_override_flat_rate(self):
        # Contribution overrides should have priority over role overrides
        Override.objects.create(
            contributor=self.contributors['jarvis'],
            role=self.roles['flatrate'],
            rate=80
        )
        ContributionOverride.objects.create(
            contribution=self.contributions['flatrate'],
            rate=44
        )
        self.assertEqual(self.contributions['flatrate'].get_override, 44)
        self.assertEqual(self.contributions['flatrate'].get_pay, 44)

    def test_get_rate_feature_type(self):
        contribution = self.contributions['featuretype']['tvclub']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, FeatureTypeRate)
        self.assertEqual(rate.rate, 30)

        contribution = self.contributions['featuretype']['news']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, FeatureTypeRate)
        self.assertEqual(rate.rate, 50)

    def test_get_rate_multiple_feature_types(self):
        for i in range(20):
            FeatureType.objects.create(name='FeatureType#{}'.format(i))
        role = ContributorRole.objects.create(name='FeatureKing', payment_type=1)
        contribution = Contribution.objects.create(
            content=self.content['c1'],
            contributor=self.contributors['jarvis'],
            role=role
        )
        tvclub_rate = FeatureTypeRate.objects.get(
            role=role, feature_type=self.feature_types['tvclub']
        )
        tvclub_rate.rate = 200
        tvclub_rate.save()
        rate = contribution.get_rate()
        self.assertEqual(rate.rate, 200)

    def test_get_pay_feature_type(self):
        contribution = self.contributions['featuretype']['tvclub']
        self.assertEqual(contribution.get_pay, 30)

        contribution = self.contributions['featuretype']['news']
        self.assertEqual(contribution.get_pay, 50)

    def test_get_override_feature_type(self):
        tvclub_override = FeatureTypeOverride.objects.create(
            feature_type=self.feature_types['tvclub'],
            rate=22
        )
        override = FeatureTypeOverrideProfile.objects.create(role=self.roles['featuretype'])
        override.feature_types.add(tvclub_override)
        override.save()

        contribution = self.contributions['featuretype']['tvclub']
        self.assertEqual(contribution.get_override, 22)
        self.assertEqual(contribution.get_pay, 22)

        tvclub_override_2 = FeatureTypeOverride.objects.create(
            feature_type=self.feature_types['tvclub'],
            rate=33
        )
        override.feature_types.add(tvclub_override_2)
        override.save()

        contribution = self.contributions['featuretype']['tvclub']
        self.assertEqual(contribution.get_override, 33)
        self.assertEqual(contribution.get_pay, 33)

    def test_get_rate_hourly(self):
        contribution = self.contributions['hourly']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, HourlyRate)
        self.assertEqual(rate.rate, 60)

    def test_get_pay_hourly(self):
        contribution = self.contributions['hourly']
        self.assertEqual(contribution.minutes_worked, 30)
        self.assertEqual(contribution.get_pay, 30)

    def test_get_rate_manual(self):
        contribution = self.contributions['manual']
        rate = contribution.get_rate()
        self.assertIsInstance(rate, ManualRate)
        self.assertEqual(rate.rate, 1000)

    def test_get_pay_manual(self):
        contribution = self.contributions['manual']
        self.assertEqual(contribution.get_pay, 1000)

    def test_force_payment(self):
        content = Content.objects.create(title='Hello my friend')
        contribution = Contribution.objects.create(
            content=content,
            contributor=self.contributors['jarvis'],
            role=self.roles['flatrate'],
            force_payment=False
        )
        now = timezone.now()
        start_date = datetime.datetime(
            year=2016,
            month=9,
            day=1,
            tzinfo=now.tzinfo
        )
        end_date = datetime.datetime(
            year=2016,
            month=9,
            day=30,
            tzinfo=now.tzinfo
        )
        include, exclude = get_forced_payment_contributions(start_date, end_date)
        self.assertEqual(include.count(), 0)
        self.assertEqual(exclude.count(), 0)

        contribution.force_payment = True
        contribution.save()
        include, exclude = get_forced_payment_contributions(start_date, end_date)
        self.assertIn(contribution, include)
        self.assertEqual(exclude.count(), 0)

        pay_date = datetime.datetime(
            year=2016,
            month=9,
            day=15,
            tzinfo=now.tzinfo
        )
        contribution.payment_date = pay_date
        contribution.save()
        include, exclude = get_forced_payment_contributions(start_date, end_date)
        self.assertIn(contribution, include)
        self.assertEqual(exclude.count(), 0)

        contribution.payment_date = pay_date - timezone.timedelta(days=1000)
        contribution.save()
        include, exclude = get_forced_payment_contributions(start_date, end_date)
        self.assertIn(contribution, exclude)
        self.assertEqual(include.count(), 0)
