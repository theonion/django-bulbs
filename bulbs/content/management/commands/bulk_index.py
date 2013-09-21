import json
import requests
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.conf import settings

from elasticutils import get_es
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyelasticsearch.client import JsonEncoder

import bulbs.content.models
from bulbs.content.models import Content, Tag
from bulbs.content.management import sync_es


class Command(NoArgsCommand):
    help = 'Bulk indexes all Content and Tag instances.'
    option_list = NoArgsCommand.option_list + (
        make_option('--purge',
            action='store_true',
            dest='purge',
            default=False,
            help='Remove all existing data'),
        make_option('--chunk',
            type=int,
            dest='chunk',
            default=250,
            help='The chunk size to index with'),
    )

    def purge(self):
        try:
            # Kill ES
            self.es.delete_index(settings.ES_INDEXES.get('default'))
        except ElasticHttpNotFoundError:
            pass
        sync_es(bulbs.content.models)

    def handle(self, **options):
        self.index_name = settings.ES_INDEXES.get('default')
        self.es = get_es(urls=settings.ES_URLS)
        bulk_endpoint = "%s/_bulk" % settings.ES_URLS[0]

        chunk_size = options.get("chunk")
        if options.get("purge"):
            self.purge()


        for klass in (Content, Tag):
            num_processed = 0
            instance_count = klass.objects.all().count()       
            while num_processed < instance_count:
                payload = []

                for instance in klass.objects.order_by('id').iterator():
                    metadata = {
                        "index": {
                            "_index": self.index_name,
                            "_type": instance.get_mapping_type_name(),
                            "_id": instance.id
                        }
                    }
                    payload.append(json.dumps(metadata, cls=JsonEncoder, use_decimal=True))
                    source = instance.extract_document()
                    payload.append(json.dumps(source, cls=JsonEncoder, use_decimal=True))
                    if chunk_size == (len(payload)/2) or ((len(payload)/2) + num_processed == instance_count):
                        r = requests.post(bulk_endpoint, data="\n".join(payload))
                        if r.status_code != 200:
                            raise Exception(r.json())
                        num_processed += chunk_size
                        print('Processed %d %s items' % (
                            num_processed, klass.__name__
                        ))
                        payload = []
