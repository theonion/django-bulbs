from celery import shared_task

from .email import EmailReport
from .models import Contribution


@shared_task(default_retry_delay=5)
def update_role_rates(contributor_role_pk):
    for contribution in Contribution.objects.filter(contributor__pk=contributor_role_pk):
        contribution.index()


def run_contributor_email_report():
    report = EmailReport()
