"""celery tasks for contributions."""
from celery import shared_task

from .email import send_byline_email, EmailReport
from .models import Contribution


@shared_task(default_retry_delay=5)
def update_role_rates(contributor_role_pk):
    for contribution in Contribution.objects.filter(contributor__pk=contributor_role_pk):
        contribution.index()


@shared_task(default_retry_delay=5)
def run_contributor_email_report(**kwargs):
    report = EmailReport(**kwargs)
    report.send_mass_contributor_emails()


@shared_task(default_retry_delay=5)
def run_send_byline_email(to, content_id, previous_byline, new_byline):
    send_byline_email(to, content_id, previous_byline, new_byline)
