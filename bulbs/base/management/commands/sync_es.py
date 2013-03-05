from django.core.management.base import BaseCommand
from django.conf import settings

import rawes
import copy


class Command(BaseCommand):
    args = ''
    help = 'Syncs the data model with Elastic Search'

    def handle(self, *args, **options):
        server_conf = copy.deepcopy(settings.ES_SERVER)
        index_name = server_conf['path']
        del server_conf['path']
        es = rawes.Elastic(**server_conf)

        if es.head(index_name) is False:
            es.put(index_name)

        if es.head('%s/content' % index_name) is False:
            mapping_data = {
                "content": {
                    "properties": {
                        "title": {"type": "string"},
                        "slug": {"type": "string", "index": "not_analyzed"},
                        "created": {"type": "date"},
                        "modified": {"type": "date"},
                        "description": {"type": "string"},
                        "byline": {"type": "string"},
                        "subhead": {"type": "string"},
                        "tags": {"type": "string", "index_name": "tag"},
                        "content_type": {"type": "string"},
                    }
                }
            }
            es.put('%s/content/_mapping' % index_name, data=mapping_data)
