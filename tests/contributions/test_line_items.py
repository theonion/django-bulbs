from dateutil import parser

from django.core.urlresolvers import reverse
from django.utils import timezone

from bulbs.contributions.models import LineItem
from bulbs.utils.test import BaseAPITestCase


class LineItemTestCase(BaseAPITestCase):

    def setUp(self):
        super(LineItemTestCase, self).setUp()
        self.list_endpoint = reverse("line-items-list")

    def test_post_success(self):
        data = {
            "contributor": self.admin.pk,
            "amount": 20,
            "note": "Pretty Good",
            "payment_date": timezone.now().isoformat()
        }
        resp = self.api_client.post(self.list_endpoint, data=data)
        self.assertEqual(resp.status_code, 201)

    def test_list_success(self):
        for i in range(40):
            LineItem.objects.create(
                contributor=self.admin,
                amount=i,
                payment_date=timezone.now() - timezone.timedelta(days=i)
            )
        resp = self.api_client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 40)

    def test_start_end_filter_query(self):
        now = timezone.now()
        this_month_end = (timezone.datetime(
            day=1, month=now.month + 1, year=now.year) - timezone.timedelta(days=1)
        )
        this_month_start = timezone.datetime(day=1, month=now.month, year=now.year)
        last_month_end = this_month_start - timezone.timedelta(days=1)
        last_month_start = timezone.datetime(
            day=1, month=last_month_end.month, year=last_month_end.year
        )
        for i in range(20):
            LineItem.objects.create(
                contributor=self.admin,
                amount=i,
                payment_date=this_month_start + timezone.timedelta(days=i)
            )
            LineItem.objects.create(
                contributor=self.admin,
                amount=i,
                payment_date=last_month_start + timezone.timedelta(days=i)
            )

        resp = self.api_client.get(
            self.list_endpoint, {
                "start": this_month_start.date().isoformat(),
                "end": this_month_end.date().isoformat()
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)

        resp = self.api_client.get(
            self.list_endpoint, {
                "start": last_month_start.date().isoformat(),
                "end": last_month_end.date().isoformat()
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 20)

        resp = self.api_client.get(
            self.list_endpoint, {"start": last_month_start.date().isoformat()}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 40)

    def test_ordering(self):
        for i in range(40):
            LineItem.objects.create(
                contributor=self.admin,
                amount=i,
                payment_date=timezone.now() + timezone.timedelta(days=i)
            )
        resp = self.client.get(self.list_endpoint)
        self.assertEqual(resp.status_code, 200)
        previous = None
        for instance in resp.data["results"]:
            payment_date = parser.parse(instance["payment_date"])
            if previous is None:
                previous = payment_date
            else:
                self.assertLess(payment_date, previous)
                previous = payment_date
