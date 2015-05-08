from django.core.management.base import BaseCommand
from bulbs.special_coverage.models import SpecialCoverage


class Command(BaseCommand):
    help = 'Indexes all Special Coverage sections'

    def handle(self, *args, **options):
        for sc in SpecialCoverage.objects.filter(active=True):
            if sc.query:
                sc._save_percolator()
