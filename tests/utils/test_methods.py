from datetime import datetime
from unittest import TestCase

from django.utils import timezone

from bulbs.utils.methods import datetime_to_epoch_seconds


class TimeTests(TestCase):

    def test_datetime_to_epoch_seconds(self):
        self.assertEqual(1455119441.0,
                         datetime_to_epoch_seconds(datetime(2016, 2, 10, 15, 50, 41, tzinfo=timezone.utc)))
