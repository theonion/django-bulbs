from django.core.management.base import BaseCommand
from django.utils import timezone

from bulbs.content.models import Content, FeatureType
from bulbs.content.tasks import post_to_instant_articles_api


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('feature', nargs="+", type=str)

    def handle(self, *args, **options):
        feature_types = FeatureType.objects.filter(instant_article=True)

        feature = options['feature'][0]
        if feature:
            feature_types = feature_types.filter(slug=feature)

        for ft in feature_types:
                # All unmigrated published content belonging to feature type
                content = Content.objects.filter(
                    feature_type=ft,
                    published__isnull=False,
                    published__lte=timezone.now(),
                    instant_article_id__isnull=True)

                for c in content:
                    post_to_instant_articles_api.delay(c.id)
