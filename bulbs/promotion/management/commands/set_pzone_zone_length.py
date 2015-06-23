from django.core.management.base import BaseCommand, CommandError

from bulbs.promotion.models import PZone


pzone_names = [pzone.name for pzone in PZone.objects.all()]


class Command(BaseCommand):

    help = "Set the length of a pzone."

    def add_arguments(self, parser):

        parser.add_argument(
            "zone_name",
            help="Name of zone to set the zone_length for.",
            choices=pzone_names,
            type=str)

        parser.add_argument(
            "zone_length",
            help="Pzone's new zone_length.",
            type=int)

    def handle(self, *args, **options):

        zone_length = options["zone_length"]
        if zone_length < 0:
            raise CommandError("zone_length must be a positive number.")

        pzone = PZone.objects.get(name=options["zone_name"])
        pzone.zone_length = zone_length
        pzone.save()

        print("PZone '{}' length updated to {}".format(pzone.name, pzone.zone_length))
