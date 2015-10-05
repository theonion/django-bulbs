from .models import Contribution


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
