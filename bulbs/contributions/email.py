"""Module to generate and send a report to contributors containing a log of their contributions."""
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()  # NOQA


class EmailReport(object):
    """Generate an email report for contributors."""

    def __init__(self, **kwargs):  # NOQA
        self.start, self.end = self.get_start_and_end_dates(**kwargs)

        self._contributors = []

    def get_start_and_end_dates(self, **kwargs):
        """
        Return start and end date for the given report.

        Uses the beginning of the current month by default.
        """
        now = timezone.now()
        month = kwargs.get("month", now.month)
        year = kwargs.get("year", now.year)
        start = timezone.datetime(day=1, month=month, year=year)
        next_month = (month + 1) % 12
        if next_month == 1:
            year += 1
        end = timezone.datetime(day=1, month=next_month, year=year)
        return start, end

    def get_contributors(self):
        """Return a list of contributors with contributions between the start/end dates."""
        return User.objects.filter(
            contributions__content__published__gte=self.start,
            contributions__content__published__lt=self.end
        ).distinct()

    def get_contributions_by_contributor(self, contributor, **kwargs):
        """Return a list of all contributions associated with a contributor for a given month."""
        return contributor.contributions.filter(
            content__published__gte=self.start, content__published__lt=self.end
        )

    @property
    def contributors(self):
        """Property to retrieve or access the list of contributors."""
        if not self._contributors:
            self._contributors = self.get_contributors()
        return self._contributors
