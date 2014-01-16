import json

from django.core.management.base import BaseCommand
from elasticutils import get_es

from bulbs.indexable.conf import settings
from bulbs.indexable.models import polymorphic_indexable_registry

class Command(BaseCommand):
    help = "Dump the indexable settings and mappings to a bash script"

    def handle(self, **options):
        es = get_es(urls=settings.ES_URLS)

        self.stdout.write("#!/bin/bash")
        self.stdout.write("ES_HOST=$1")

        aliases = es.aliases()
        for index_name in aliases:
            index_aliases = aliases[index_name]["aliases"]
            if index_aliases:
                index_alias = index_aliases.keys()[0]
                self.stdout.write("curl -XPUT http://$ES_HOST:9200/%s -d '%s'" % (index_name, json.dumps(settings.ES_SETTINGS)))
                self.stdout.write('curl -XPOST http://$ES_HOST:9200/_aliases -d \'{"actions": [{"add": {"index": "%s", "alias": "%s"}}]}\'' % (index_name, index_alias))

        for name, model in polymorphic_indexable_registry.all_models.items():
            self.stdout.write("curl -XPUT http://$ES_HOST:9200/%s/%s/_mapping -d '%s'" % (
                    model.get_index_name(),
                    model.get_mapping_type_name(),
                    json.dumps(model.get_mapping())
                )
            )