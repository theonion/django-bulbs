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
    args = "<?index_suffix>"
    option_list = BaseCommand.option_list + (
        make_option("--chunk",
            type=int,
            dest="chunk",
            default=250,
            help="The chunk size to index with"),
        make_option("--index-suffix",
            type=str,
            dest="index_suffix",
            default="",
            help="Suffix for ES index."),
    )

    def handle(self, *args, **options):
        self.es = get_es(urls=settings.ES_URLS)
        bulk_endpoint = "%s/_bulk" % settings.ES_URLS[0]

        chunk_size = options.get("chunk")
        index_suffix = options.get("index_suffix")

        if index_suffix:
            index_suffix = "_" + index_suffix

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
                        "_index": instance.get_index_name() + index_suffix,
                        "_type": instance.get_mapping_type_name(),
                        "_id": instance.pk
                    }
                }
                payload.append(json.dumps(meta, cls=JsonEncoder, use_decimal=True))
                doc = instance.extract_document()
                payload.append(json.dumps(doc, cls=JsonEncoder, use_decimal=True))
                if len(payload) / 2 == chunk_size:
                    r = requests.post(bulk_endpoint, data="\n".join(payload) + "\n")
                    if r.status_code != 200:
                        print(payload)
                        print(r.json())
                    else:
                        # make sure it indexed everything:
                        result = r.json()
                        good_items = [item for item in result["items"] if item["index"].get("ok", False)]
                        if len(good_items) != len(payload) // 2:
                            self.stdout.write("Bulk indexing error! Item count mismatch.")
                            bad_items = [item for item in result["items"] if not item["index"].get("ok", False)]
                            self.stdout.write("These were rejected: %s" % str(bad_items))
                            return "Bulk indexing failed."
                    num_processed += (len(payload) / 2)
                    self.stdout.write("Indexed %d items" % num_processed)
                    payload = []

        if payload:
            r = requests.post(bulk_endpoint, data="\n".join(payload) + "\n")
            if r.status_code != 200:
                print(payload)
                print(r.json())
            num_processed += (len(payload) / 2)
            self.stdout.write("Indexed %d items" % num_processed)
