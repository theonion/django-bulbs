from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from bulbs.content.models import FeatureType


class Command(BaseCommand):

    help = "Set a provided FeatureType as available for Facebook Instant Articles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            dest="featuretype_slug",
            help="The slug for the desired FeatureType.",
            required=True,
            type=str
        )

    def handle(self, *args, **kwargs):
        featuretype_slug = kwargs.get("featuretype_slug")
        featuretype = get_object_or_404(FeatureType, slug=featuretype_slug)
        if not featuretype.instant_article:
            featuretype.instant_article = True
            featuretype.save()
            # celery is not configured during commands.
            for content in featuretype.content_set.all():
                content.index()
