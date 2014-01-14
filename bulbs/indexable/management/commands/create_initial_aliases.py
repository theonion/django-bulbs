from django.core.management.base import BaseCommand
from elasticutils.contrib.django import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from bulbs.indexable.models import polymorphic_indexable_registry


class Command(BaseCommand):
    help = "Adds appropriate aliases to the 'avclub' index. Delete after we're done."
    args = "<index_suffix>"

    def handle(self, **options):
        aliases = set()
        for name, model in polymorphic_indexable_registry.all_models.items():
            aliases.add(model.get_index_name())
        # add our new aliases
        alias_actions = [] 
        for alias in aliases:
            alias_actions.append({
                "add": {
                    "alias": alias,
                    "index": "avclub"
                }
            })
        get_es().update_aliases(dict(actions=alias_actions))
        