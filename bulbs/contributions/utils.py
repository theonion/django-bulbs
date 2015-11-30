from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Contribution, ContributorRole, FreelanceProfile, FEATURETYPE


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


def import_payroll_names(lookup_string):
    User = get_user_model()
    lookup_string = lookup_string.decode('unicode_escape').encode('ascii', 'ignore')
    rows = lookup_string.split('\n')
    rows = [row.rstrip('\n').rstrip('\r') for row in rows]
    rows = [row.split('\t') for row in rows]
    for row in rows:
        full_name, payroll_name = row[0], row[1]
        ordered_name = full_name.strip().split(' ')
        if len(ordered_name) == 2:
            first_name, last_name = ordered_name[0], ordered_name[1]
            qs = User.objects.filter(first_name=first_name, last_name=last_name)
            if qs.count() != 1:
                # print 'Cannot find user: {}'.format(full_name)
                return
            else:
                user = qs.first()
                profile = getattr(user, 'freelanceprofile', None)
                if not profile:
                    profile = FreelanceProfile.objects.create(
                        contributor=user,
                        is_freelance=True
                    )
                else:
                    profile.payroll_name = payroll_name.strip()
                    profile.save()
