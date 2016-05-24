"""celery tasks for contributions."""
from celery import shared_task

from bulbs.content.models import Content
from .email import send_byline_email, EmailReport
from .models import Contribution, FreelanceProfile


@shared_task(default_retry_delay=5)
def check_and_update_freelanceprofiles(content_id):
    content = Content.objects.get(id=content_id)
    for author in content.authors.all():
        profile = getattr(author, "freelanceprofile", None)
        if profile is None:
            FreelanceProfile.objects.create(contributor=author)


@shared_task(default_retry_delay=5)
def update_role_rates(contributor_role_pk):
    for contribution in Contribution.objects.filter(contributor__pk=contributor_role_pk):
        contribution.index()


@shared_task(default_retry_delay=5)
def run_contributor_email_report(**kwargs):
    report = EmailReport(**kwargs)
    report.send_mass_contributor_emails()


@shared_task(default_retry_delay=5)
def run_send_byline_email(content_id, removed_author_pks):
    content = Content.objects.get(id=content_id)
    removed_bylines = content.authors.filter(pk__in=removed_author_pks)
    send_byline_email(content, removed_bylines)
