import json
import requests
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import models

from elasticutils import get_es
from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyelasticsearch.client import JsonEncoder

from bulbs.indexable import PolymorphicIndexable
from bulbs.indexable.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = "Bulk indexes all Content and Tag instances."
    option_list = BaseCommand.option_list + (
        make_option("--purge",
            action="store_true",
            dest="purge",
            default=False,
            help="Remove all existing data"),
        make_option("--chunk",
            type=int,
            dest="chunk",
            default=250,
            help="The chunk size to index with"),
    )

    def kill_indexes(self, *args):
        # TODO: use the indexable cache, instead of this POS
        indexes = []
        for app in models.get_apps():
            for model in models.get_models(app):
                if issubclass(model, PolymorphicIndexable):
                    if model.get_index_name() not in indexes:
                        indexes.append(model.get_index_name())

        es = get_es(urls=settings.ES_URLS)
        for index in indexes:
            try:
                es.delete_index(index)
            except ElasticHttpNotFoundError:
                pass


    def handle(self, *args, **options):
        self.es = get_es(urls=settings.ES_URLS)
        bulk_endpoint = "%s/_bulk" % settings.ES_URLS[0]

        chunk_size = options.get("chunk")
        if options.get("purge"):
            self.kill_indexes(*args)
            call_command("synces")  # This will cause all the indexes to get recreated, since that all runs on signals.

        all_models_to_index = set()
        if len(args):
            for app_name in args:
                for model in models.get_models(models.get_app(app_name)):
                    if issubclass(model, PolymorphicIndexable):
                        all_models_to_index.add(model)
        else:
            for app in models.get_apps():
                for model in models.get_models(app):
                    if issubclass(model, PolymorphicIndexable):
                        all_models_to_index.add(model)

        # remove redundant subclasses since the instance_of query will select them
        models_to_index = set()
        for model_i in all_models_to_index:
            should_add = True
            for model_j in all_models_to_index:
                if model_i != model_j and issubclass(model_i, model_j):
                    should_add = False
                    break
            if should_add:
                models_to_index.add(model_i)

        self.stdout.write(u"Indexing models: %s" % ', '.join([m.__name__ for m in models_to_index]))

        num_processed = 0
        payload = []
        for model in models_to_index:
            for instance in model.objects.instance_of(model).order_by("id").iterator():     
                meta = {
                    "index": {
                        "_index": instance.get_index_name(),
                        "_type": instance.get_mapping_type_name(),
                        "_id": instance.pk
                    }
                }
                payload.append(json.dumps(meta, cls=JsonEncoder, use_decimal=True))
                doc = instance.extract_document()
                payload.append(json.dumps(doc, cls=JsonEncoder, use_decimal=True))
                if len(payload) / 2 == chunk_size:
                    r = requests.post(bulk_endpoint, data="\n".join(payload) + '\n')
                    if r.status_code != 200:
                        print(payload)
                        print(r.json())
                    num_processed += (len(payload) / 2)
                    self.stdout.write("Indexed %d items" % num_processed)
                    payload = []

        if payload:
            r = requests.post(bulk_endpoint, data="\n".join(payload) + '\n')
            if r.status_code != 200:
                print(payload)
                print(r.json())
            num_processed += (len(payload) / 2)
            self.stdout.write("Indexed %d items" % num_processed)
