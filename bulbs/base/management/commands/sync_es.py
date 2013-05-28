from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from django.db import models

from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError


from bulbs.base.models import Contentish, Tagish


class Command(NoArgsCommand):
    args = ''
    help = "Create the Elastic Search indexes and mappings tables for all apps in INSTALLED_APPS."

    def handle(self, **options):
        self.style = no_style()

        es = get_es(urls=settings.ES_URLS)
        index = settings.ES_INDEXES.get('default')
        try:
            es.create_index(index)
        except IndexAlreadyExistsError:
            pass

        for app in models.get_apps():
            for model in models.get_models(app, include_auto_created=True):
                if isinstance(model(), Contentish):
                    # print("Syncing: %s" % model.get_mapping_type_name())
                    es.put_mapping(
                        index,
                        model.get_mapping_type_name(),
                        model.get_mapping()
                    )

        tag_mapping = {
            "tag": {
                "properties": {
                    "name": {"type": "string"},
                    "slug": {"type": "string", "index": "not_analyzed"},
                    "content_type": {"type": "string", "index": "not_analyzed"},
                    "object_id": {"type": "integer"}
                }
            }
        }
        es.put_mapping(index, "tag", tag_mapping)
