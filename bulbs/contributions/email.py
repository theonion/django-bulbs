"""Module to generate and send a report to contributors containing a log of their contributions."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone


User = get_user_model()  # NOQA


# Define constants.
CONTRIBUTION_SETTINGS = getattr(settings, "CONTRIBUTIONS", {})
EMAIL_SETTINGS = CONTRIBUTION_SETTINGS.get("EMAIL", {})
DEFAULT_SUBJECT = "Contribution Report."
TEMPLATE = "reporting/__contribution_report.html"


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

        # If we incremented at the end of the year. It's a new year!!!!!
        if next_month == 1:
            year += 1

        end = timezone.datetime(day=1, month=next_month, year=year)
        return start, end

    def send_contributor_email(self, contributor):
        """Send an EmailMessage object for a given contributor."""
        body = self.get_email_body(contributor)
        mail = EmailMultiAlternatives(
            subject=EMAIL_SETTINGS.get("SUBJECT", DEFAULT_SUBJECT),
            from_email=EMAIL_SETTINGS.get("FROM"),
            headers={"Reply-To": EMAIL_SETTINGS.get("REPLY_TO")}
        )
        mail.attach_alternative(body, "text/html")
        if EMAIL_SETTINGS.get("ACTIVE", False):
            mail.to = [contributor.email]
        else:
            mail.to = EMAIL_SETTINGS.get("TO")
        resp = mail.send()

    def send_mass_contributor_emails(self):
        """Send report email to all relevant contributors."""
        # If the report configuration is not active we only send to the debugging user.
        if EMAIL_SETTINGS.get("ACTIVE", False):
            for contributor in self.contributors:
                self.send_contributor_email(contributor)
        else:
            for email in EMAIL_SETTINGS.get("TO", []):
                self.send_contributor_email(User.objects.get(email=email))

    def get_email_body(self, contributor):  # NOQA
        contributions = self.get_contributions_by_contributor(contributor)
        total = sum([contribution.pay for contribution in contributions if contribution.pay])
        contribution_types = {}
        for contribution in contributions:
            contribution_types[contribution] = contribution.content._meta.concrete_model.__name__
        context = {
            "content_type": contribution.content._meta.concrete_model.__name__,
            "contributor": contributor,
            "contributions": contribution_types,
            "next_day": timezone.now() + timezone.timedelta(days=1),
            "total": total
        }
        return loader.render_to_string(TEMPLATE, context)

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
