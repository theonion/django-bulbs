"""celery tasks for contributions."""
from celery import shared_task

from bulbs.content.models import Content
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
    from .email import EmailReport
    report = EmailReport(**kwargs)
    report.send_mass_contributor_emails()


@shared_task(default_retry_delay=5)
def check_and_run_send_byline_email(content_id, new_byline):
    from .email import send_byline_email
    content = Content.objects.get(id=content_id)
    removed_bylines = content.authors.exclude(pk__in=[c.id for c in new_byline])
    if removed_bylines:
        send_byline_email(content, removed_bylines)
