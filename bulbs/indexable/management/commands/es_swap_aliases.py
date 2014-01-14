from django.core.management.base import BaseCommand
from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from bulbs.indexable.models import polymorphic_indexable_registry


class Command(BaseCommand):
    help = "Updates elasticsearch index aliases."
    args = "<index_suffix>"

    def handle(self, index_suffix, **options):
        index_suffix = '_' + index_suffix
        indexes = {}
        for name, model in polymorphic_indexable_registry.all_models.items():
            alias = model.get_index_name()
            index = alias + index_suffix
            if alias not in indexes:
                indexes[alias] = index

        es = get_es()
        alias_actions = []
        # remove existing indexes using the aliases we want
        existing_aliases = es.aliases()
        for index, aliases in existing_aliases.items():
            for alias, new_index in indexes.items():
                if alias in aliases['aliases']:
                    alias_actions.append({
                        "remove": {
                            "alias": alias,
                            "index": index
                        }
                    })
        # add our new aliases
        for alias, index in indexes.items():
            alias_actions.append({
                "add": {
                    "alias": alias,
                    "index": index
                }
            })
        es.update_aliases(dict(actions=alias_actions))
        
