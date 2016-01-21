from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import SpecialCoverage


class Command(BaseCommand):
    help = "Migrates Special Coverages to published"

    def get_month_start_date(self):
        """Returns the first day of the current month"""
        now = timezone.now()
        return timezone.datetime(day=1, month=now.month, year=now.year, tzinfo=now.tzinfo)

    def get_absurd_end_date(self):
        """
        To give ourselves a buffer, we are setting the initial end_date to 5 years in the future.
        """
        now = timezone.now()
        return timezone.datetime(day=1, month=now.month, year=now.year + 5, tzinfo=now.tzinfo)

    def get_active_special_coverages(self):
        return SpecialCoverage.objects.filter(active=True)

    def update_special_coverage_instance(self, instance, **kwargs):
        for attr, value in kwargs.items():
            if not hasattr(instance, attr):
                raise AttributeError(
                    """{0} has no attribute {1}.""".format(instance._meta.model.__name__, attr)
                )
            setattr(instance, attr, value)
        instance.save()
        return instance

    def publish_active_special_coverages(self):
        start = self.get_month_start_date()
        end = self.get_absurd_end_date()
        for sc in self.get_active_special_coverages():
            active = getattr(sc, "active", None)
            if active is None:
                raise AttributeError(
                    """Special Coverage no longer has an active attribute."""
                )
            self.update_special_coverage_instance(sc, start_date=start, end_date=end)

    def handle(self, *args, **kwargs):
        self.publish_active_special_coverages()
