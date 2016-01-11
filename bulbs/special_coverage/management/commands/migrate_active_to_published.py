from django.core.management.base import BaseCommand

from ...utils import publish_active_special_coverages


class Command(BaseCommand):
    help = "Migrates Special Coverages to published"

    def handle(self, *args, **kwargs):
        publish_active_special_coverages()
