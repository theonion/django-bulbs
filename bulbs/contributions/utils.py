from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Contribution, ContributorRole, FreelanceProfile, FEATURETYPE


def merge_roles(dominant_name, deprecated_name):
    """
    Merges a deprecated role into a dominant role.
    """
    dominant_qs = ContributorRole.objects.filter(name=dominant_name)
    if not dominant_qs.exists() or dominant_qs.count() != 1:
        return
    dominant = dominant_qs.first()
    deprecated_qs = ContributorRole.objects.filter(name=deprecated_name)
    if not deprecated_qs.exists() or deprecated_qs.count() != 1:
        return
    deprecated = deprecated_qs.first()

    # Update Rates
    if not dominant.flat_rates.exists() and deprecated.flat_rates.exists():
        flat_rate = deprecated.flat_rates.first()
        flat_rate.role = dominant
        flat_rate.save()

    if not dominant.hourly_rates.exists() and deprecated.hourly_rates.exists():
        hourly_rate = deprecated.hourly_rates.first()
        hourly_rate.role = dominant
        hourly_rate.save()

    for ft_rate in deprecated.feature_type_rates.all():
        dom_ft_rate = dominant.feature_type_rates.filter(feature_type=ft_rate.feature_type)

        if dom_ft_rate.exists() and dom_ft_rate.first().rate == 0:
            dom_ft_rate.first().delete()

        if not dom_ft_rate.exists():
            ft_rate.role = dominant
            ft_rate.save()

    # Update contributions
    for contribution in deprecated.contribution_set.all():
        contribution.role = dominant
        contribution.save()

    # Update overrides
    for override in deprecated.overrides.all():
        dom_override_qs = dominant.overrides.filter(contributor=override.contributor)
        if not dom_override_qs.exists():
            override.role = dominant
            override.save()
        else:
            dom_override = dom_override_qs.first()
            for flat_override in override.override_flatrate.all():
                flat_override.profile = dom_override
                flat_override.save()
            for hourly_override in override.override_hourly.all():
                hourly_override.profile = dom_override
                hourly_override.save()
            for feature_type_override in override.override_feature_type.all():
                feature_type_override.profile = dom_override
                feature_type_override.save()


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
    user = get_user_model()
    lookup_string = lookup_string.decode('unicode_escape').encode('ascii', 'ignore')
    rows = lookup_string.split('\n')
    rows = [row.rstrip('\n').rstrip('\r') for row in rows]
    rows = [row.split('\t') for row in rows]
    for row in rows:
        full_name, payroll_name = row[0], row[1]
        ordered_name = full_name.strip().split(' ')
        if len(ordered_name) == 2:
            first_name, last_name = ordered_name[0], ordered_name[1]
            qs = user.objects.filter(first_name=first_name, last_name=last_name)
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
