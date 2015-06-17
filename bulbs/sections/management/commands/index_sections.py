from django.core.management.base import BaseCommand
from bulbs.sections.models import Section


class Command(BaseCommand):
    help = 'Indexes all section objects in the .percolator document'

    def handle(self, *args, **options):
        for section in Section.objects.all():
            if section.query is not None or section.query != {}:
                section._save_percolator()