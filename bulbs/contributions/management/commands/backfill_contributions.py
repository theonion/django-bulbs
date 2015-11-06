import argparse

from django.core.management.base import BaseCommand
from django.utils import timezone

from bulbs.content.models import Content
from bulbs.contributions.models import ContributorRole


def valid_date(s):
    try:
        return timezone.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):

    help = "add missing contributions from authors of the previous month."
    default_role = ContributorRole.objects.first()
    count = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '-start',
            '--start',
            help='The Start Date - format YYYY-MM-DD',
            required=False,
            type=valid_date
        )
        parser.add_argument(
            '-end',
            '--end',
            help='The End Date - format YYYY-MM-DD',
            required=False,
            type=valid_date
        )

    def get_date_range(self):
        now = timezone.now()
        month_start = timezone.datetime(
            year=now.year,
            month=now.month,
            day=1
        )
        return month_start, now

    def get_content_list(self, start, end):
        return Content.objects.filter(published__range=(start, end))

    def process_content_contributions(self, content):
        for author in content.authors.all():
            contribution_qs = content.contributions.filter(contributor=author)
            if not contribution_qs.exists():
                content.contributions.create(
                    contributor=author,
                    role=self.default_role
                )
                self.count += 1

    def handle(self, *args, **kwargs):
        if not self.default_role:
            self.stdout.write('No role available for backfill')
            return

        default_start, default_end = self.get_date_range()
        start = kwargs['start'] if kwargs['start'] else default_start
        end = kwargs['end'] if kwargs['end'] else default_end
        content_qs = self.get_content_list(start, end)
        for content in content_qs.all():
            self.process_content_contributions(content)
        self.stdout.write(
            '{0} contributions created between {1} - {2}'.format(self.count, start, end)
        )
