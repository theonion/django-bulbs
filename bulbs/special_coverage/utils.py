from django.utils import timezone

from bulbs.utils.methods import get_central_now
from .models import SpecialCoverage


def get_month_start_date():
    """Returns the first day of the current month"""
    now = get_central_now()
    return timezone.datetime(day=1, month=now.month, year=now.year, tzinfo=now.tzinfo)


def get_absurd_end_date():
    """To give ourselves a buffer, we are setting the initial end_date to 5 years in the future."""
    now = get_central_now()
    return timezone.datetime(day=1, month=now.month, year=now.year + 5, tzinfo=now.tzinfo)


def get_active_special_coverages():
    return SpecialCoverage.objects.filter(active=True)


def update_special_coverage_instance(instance, **kwargs):
    for attr, value in kwargs.items():
        if not hasattr(instance, attr):
            raise AttributeError(
                """{0} has no attribute {1}.""".format(instance._meta.model.__name__, attr)
            )
        setattr(instance, attr, value)
    instance.save()
    return instance


def publish_active_special_coverages():
    start = get_month_start_date()
    end = get_absurd_end_date()
    for sc in get_active_special_coverages():
        active = getattr(sc, "active", None)
        if active is None:
            raise AttributeError(
                """Special Coverage no longer has an active attribute."""
            )
        update_special_coverage_instance(sc, start_date=start, end_date=end)
