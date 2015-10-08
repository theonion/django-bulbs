from django.conf import settings

from .models import Contribution, ContributorRole, FEATURETYPE


def get_forced_payment_contributions(start_date, end_date, qs=None):
    if not qs:
        qs = Contribution.objects.filter(force_payment=True)
    include = qs.filter(
        payment_date__range=(start_date, end_date)
    ) | qs.filter(
        payment_date__isnull=True
    )
    exclude = qs.exclude(
        payment_date__isnull=True
    ).exclude(
        payment_date__range=(start_date, end_date),
    )
    return include, exclude


def update_content_contributions(content, author):
    if not Contribution.objects.filter(content=content, contributor=author).exists():
        role_name = getattr(settings, 'DEFAULT_CONTRIBUTOR_ROLE', 'default')
        role, created = ContributorRole.objects.get_or_create(name=role_name)
        if created:
            role.payment_type = FEATURETYPE
            role.save()
        Contribution.objects.create(content=content, contributor=author, role=role)
