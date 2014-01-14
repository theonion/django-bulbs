from optparse import make_option

from django.core.management.base import BaseCommand
from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from bulbs.indexable.conf import settings
from bulbs.indexable.models import polymorphic_indexable_registry


class Command(BaseCommand):
    args = '<index_suffix>'
    help = "Creates indexes and mappings for for Indexable objects."
    option_list = BaseCommand.option_list + (
        make_option("--drop-existing-indexes",
            action="store_true",
            dest="drop_existing_indexes",
            default=False,
            help="Recreate existing indexes"
        ),
        make_option("--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force a close and reopen to update analysis settings"
        ),
    )

    def handle(self, index_suffix, **options):
        index_suffix = '_' + index_suffix
        indexes = {}
        for name, model in polymorphic_indexable_registry.all_models.items():
            index = model.get_index_name() + index_suffix
            if index not in indexes:
                indexes[index] = {}
            indexes[index].update(model.get_mapping())

        es = get_es(urls=settings.ES_URLS)

        for index, mappings in indexes.items():
            keep_trying = True
            num_tries = 0
            while keep_trying and num_tries < 2:
                keep_trying = False
                num_tries += 1
                try:
                    es.create_index(index, settings={
                        "settings": settings.ES_SETTINGS
                    })
                except IndexAlreadyExistsError:
                    try:
                        if "analysis" in settings.ES_SETTINGS:
                            live_settings = es.get_settings(index)
                            if live_settings["analysis"] != settings.ES_SETTINGS["analysis"]:
                                if options.get("force", False):
                                    es.close_index(index)
                                    es.update_settings(index, settings.ES_SETTINGS)
                                    es.open_index(index)
                                else:
                                    self.stderr.write("Index '%s' already exists and has incompatible settings. You will need to use a new suffix, or use the --force option" % index)
                    except ElasticHttpError as e:
                        if options.get("drop_existing_indexes", False):
                            es.delete_index(index)
                            keep_trying = True # loop again
                        else:
                            self.stderr.write(
                                "Index '%s' already exists and has incompatible settings." % index)
        
                except ElasticHttpError as e:
                    self.stderr.write("ES Error: %s" % e.error)

            for doctype, mapping in mappings.items():
                try:
                    es.put_mapping(index, doctype, dict(doctype=mapping))
                except ElasticHttpError as e:
                    self.stderr.write("ES Error: %s" % e.error)
