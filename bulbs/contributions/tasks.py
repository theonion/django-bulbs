from celery import shared_task

from .models import Contribution


@shared_task(default_retry_delay=5)
def update_role_rates(contributor_role_pk):
    for contribution in Contribution.objects.filter(contributor__pk=contributor_role_pk):
        contribution.index()


@shared_task(default_retry_delay=5)
def update_contribution_index_from_content(content_pk):
    for contribution in Contribution.objects.filter(content__pk=content_pk):
        contribution.save()
