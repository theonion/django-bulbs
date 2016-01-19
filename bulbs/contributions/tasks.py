from celery import shared_task


@shared_task(default_retry_delay=5)
def update_role_rates(contributor_role):
    for contribution in contributor_role.contribution_set.all():
        contribution.index()
